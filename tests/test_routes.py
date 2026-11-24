import io
import re
import sqlite3
import zipfile

import pytest

from app import create_app


def test_database_created_on_startup(tmp_path):
    db_path = tmp_path / "fresh.db"
    assert not db_path.exists()
    create_app({"TESTING": True, "DATABASE": str(db_path)})
    with sqlite3.connect(db_path) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
    assert "projects" in tables


def test_index_and_history_render(client):
    index = client.get("/")
    assert index.status_code == 200
    assert b"Unity AI Architect" in index.data
    assert b'value="Platformer"' in index.data

    history = client.get("/history")
    assert history.status_code == 200
    assert b"Recommendation History" in history.data
    assert b"No Recommendations Found" in history.data


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"project_name": ""}, b"Project Name (Game Title) is required."),
        ({"project_name": "x" * 101}, b"Project Name must be 100 characters or less."),
        ({"genre": ""}, b"Genre selection is required."),
        ({"genre": "Not A Genre"}, b"Genre selection is not valid."),
        ({"platform": "Toaster"}, b"Platform selection is not valid."),
        ({"target_audience": ""}, b"Target Audience selection is required."),
        ({"description": "Short"}, b"Game Description should be at least 20 characters"),
        ({"description": "d" * 2001}, b"Game Description must be 2000 characters or less."),
        ({"engine_choice": "skynet"}, b"Engine selection is not valid."),
    ],
)
def test_validation_failures(client, valid_form, overrides, message):
    valid_form.update(overrides)
    response = client.post("/analyze", data=valid_form)
    assert response.status_code == 400
    assert message in response.data


def test_validation_keeps_user_input_and_escapes_it(client, valid_form):
    valid_form["project_name"] = '"><script>alert(1)</script>'
    valid_form["genre"] = ""
    response = client.post("/analyze", data=valid_form)
    assert response.status_code == 400
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data


def test_full_flow_results_exports_and_delete(client, valid_form):
    response = client.post("/analyze", data=valid_form)
    assert response.status_code == 302
    assert re.fullmatch(r"/results/\d+", response.headers["Location"])
    project_id = response.headers["Location"].rsplit("/", 1)[-1]

    results = client.get(f"/results/{project_id}")
    assert results.status_code == 200
    assert b"Test Runner Game" in results.data
    assert b"PlayerController.cs" in results.data
    assert b"Download" in results.data

    export = client.get(f"/export/{project_id}")
    assert export.status_code == 200
    assert export.mimetype == "text/markdown"
    assert b"# Unity Asset Recommendation Report: Test Runner Game" in export.data
    assert b"````csharp" in export.data

    archive = client.get(f"/download-zip/{project_id}")
    assert archive.status_code == 200
    assert archive.mimetype == "application/zip"
    with zipfile.ZipFile(io.BytesIO(archive.data)) as zf:
        names = zf.namelist()
    assert any(n.startswith("Assets/Art/") for n in names)
    assert "Assets/Scripts/Managers/GameManager.cs" in names
    assert "Assets/Scripts/Gameplay/PlayerController.cs" in names
    assert "Assets/README_StarterKit.txt" in names

    history = client.get("/history")
    assert b"Test Runner Game" in history.data

    deleted = client.post(f"/delete/{project_id}", follow_redirects=True)
    assert deleted.status_code == 200
    assert b"Recommendation history deleted successfully." in deleted.data
    assert client.get(f"/results/{project_id}").status_code == 404


def test_missing_project_returns_404(client):
    for path in ("/results/999", "/export/999", "/download-zip/999"):
        assert client.get(path).status_code == 404


def test_html_in_stored_content_is_escaped(client, valid_form):
    valid_form["project_name"] = "<img src=x onerror=alert(1)>"
    valid_form["description"] = "<script>alert('xss')</script> and then some more text"
    response = client.post("/analyze", data=valid_form)
    project_id = response.headers["Location"].rsplit("/", 1)[-1]

    for path in (f"/results/{project_id}", "/history"):
        body = client.get(path).data
        assert b"<img src=x" not in body
        assert b"<script>alert('xss')" not in body


def test_history_search_and_filter(client, valid_form):
    client.post("/analyze", data=valid_form)
    other = dict(valid_form, project_name="Gem Matcher", genre="Puzzle")
    client.post("/analyze", data=other)
    client.get("/history")  # consume pending flash messages

    assert b"Gem Matcher" in client.get("/history?q=gem").data
    assert b"Test Runner Game" not in client.get("/history?q=gem").data
    assert b"Test Runner Game" in client.get("/history?genre=Platformer").data
    assert b"Gem Matcher" not in client.get("/history?genre=Platformer").data


def test_history_search_is_injection_and_wildcard_safe(client, valid_form):
    client.post("/analyze", data=valid_form)
    client.get("/history")  # consume the pending success flash message

    injected = client.get("/history", query_string={"q": "' OR 1=1 --"})
    assert injected.status_code == 200
    assert b"Test Runner Game" not in injected.data

    wildcard = client.get("/history", query_string={"q": "%"})
    assert b"Test Runner Game" not in wildcard.data


def test_unavailable_provider_falls_back_to_offline(client, valid_form):
    valid_form["engine_choice"] = "openai"  # no key configured in tests
    response = client.post("/analyze", data=valid_form, follow_redirects=True)
    assert response.status_code == 200
    assert b"offline engine was used" in response.data


def test_csrf_enforced_when_enabled(tmp_path, valid_form):
    app = create_app({"TESTING": True, "CSRF_ENABLED": True, "DATABASE": str(tmp_path / "csrf.db")})
    client = app.test_client()

    assert client.post("/analyze", data=valid_form).status_code == 400

    page = client.get("/").get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([0-9a-f]+)"', page).group(1)
    ok = client.post("/analyze", data=dict(valid_form, csrf_token=token))
    assert ok.status_code == 302


def test_security_headers(client):
    headers = client.get("/").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert "script-src 'self'" in headers["Content-Security-Policy"]
