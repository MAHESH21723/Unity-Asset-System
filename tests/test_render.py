"""Render / public-demo mode (works with no AI keys: offline engine)."""
from app import DEMO_NOTICE, create_app
from tests.conftest import VALID_FORM


def make(tmp_path):
    return create_app({"TESTING": True, "CSRF_ENABLED": False, "DATABASE": str(tmp_path / "r.db")})


def test_render_env_sets_secure_cookies(tmp_path, monkeypatch):
    monkeypatch.setenv("RENDER", "1")
    app = make(tmp_path)
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.test_client().get("/", headers={"X-Forwarded-Proto": "https"}).status_code == 200


def test_demo_banner_and_offline_analysis(tmp_path, monkeypatch):
    monkeypatch.setenv("RENDER", "1")
    monkeypatch.setenv("DEMO_DATA", "1")
    client = make(tmp_path).test_client()
    assert DEMO_NOTICE.replace("'", "&#39;") in client.get("/").get_data(as_text=True)
    form = dict(VALID_FORM, engine_choice="auto")
    response = client.post("/analyze", data=form)
    assert response.status_code == 302


def test_no_banner_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("DEMO_DATA", raising=False)
    html = make(tmp_path).test_client().get("/").get_data(as_text=True)
    assert "Public demo" not in html