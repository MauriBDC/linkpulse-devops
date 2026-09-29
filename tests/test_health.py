def test_liveness(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness(client):
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_startup_does_not_create_schema(monkeypatch):
    from fastapi.testclient import TestClient

    from app.database import Base
    from app.main import app

    def unexpected_schema_creation(*args, **kwargs):
        raise AssertionError("Application startup must not create tables")

    monkeypatch.setattr(Base.metadata, "create_all", unexpected_schema_creation)
    with TestClient(app) as client:
        assert client.get("/health/live").status_code == 200
