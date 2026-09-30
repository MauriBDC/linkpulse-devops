import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch, tmp_path):
    for name in Settings.model_fields:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.lower(), raising=False)
    monkeypatch.chdir(tmp_path)


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    settings = Settings()

    assert settings.APP_NAME == "LinkPulse API"
    assert settings.APP_ENV == "development"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.DATABASE_URL == "sqlite+pysqlite:///:memory:"


def test_settings_from_environment(monkeypatch):
    values = {
        "APP_NAME": "LinkPulse Production",
        "APP_ENV": "production",
        "DATABASE_URL": "postgresql+psycopg://example:example@database:5432/example",
        "LOG_LEVEL": "WARNING",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    assert Settings().model_dump() == values


def test_settings_from_dotenv(tmp_path):
    (tmp_path / ".env").write_text(
        "APP_NAME=LinkPulse Local\n"
        "APP_ENV=test\n"
        "DATABASE_URL=sqlite+pysqlite:///local.db\n"
        "LOG_LEVEL=DEBUG\n"
        "POSTGRES_PASSWORD=example-only\n",
        encoding="utf-8",
    )

    settings = Settings()

    assert settings.APP_NAME == "LinkPulse Local"
    assert settings.APP_ENV == "test"
    assert settings.DATABASE_URL == "sqlite+pysqlite:///local.db"
    assert settings.LOG_LEVEL == "DEBUG"


def test_environment_overrides_dotenv(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text(
        "DATABASE_URL=sqlite+pysqlite:///local.db\nLOG_LEVEL=DEBUG\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    settings = Settings()

    assert settings.DATABASE_URL == "sqlite+pysqlite:///:memory:"
    assert settings.LOG_LEVEL == "ERROR"


def test_database_url_is_required():
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings()


def test_database_url_cannot_be_empty(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")

    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings()


@pytest.mark.parametrize("field,value", [("APP_ENV", "staging"), ("LOG_LEVEL", "INVALID")])
def test_invalid_settings_are_rejected(monkeypatch, field, value):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv(field, value)

    with pytest.raises(ValidationError, match=field):
        Settings()
