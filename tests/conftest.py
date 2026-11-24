import pytest

from app import create_app

VALID_FORM = {
    "project_name": "Test Runner Game",
    "genre": "Platformer",
    "platform": "PC",
    "target_audience": "Core",
    "description": "An endless runner game with procedurally generated obstacles and jumping mechanics.",
    "engine_choice": "mock",
}


@pytest.fixture(autouse=True)
def _no_api_keys(monkeypatch):
    """Tests must never reach a real provider."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "CSRF_ENABLED": False, "DATABASE": str(tmp_path / "test.db")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_form():
    return dict(VALID_FORM)


@pytest.fixture
def project_id(client, valid_form):
    response = client.post("/analyze", data=valid_form)
    assert response.status_code == 302
    return int(response.headers["Location"].rsplit("/", 1)[-1])
