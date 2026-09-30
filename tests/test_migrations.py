import os
import subprocess
import sys
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from app.database import Base

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_initial_migration_round_trip(tmp_path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'migrations.db'}"
    env = {**os.environ, "DATABASE_URL": database_url}

    def migrate(*args):
        subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            cwd=PROJECT_ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

    engine = create_engine(database_url)
    try:
        migrate("upgrade", "head")
        with engine.connect() as connection:
            assert "links" in inspect(connection).get_table_names()
            assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        migrate("check")
        migrate("upgrade", "head")
        migrate("downgrade", "base")
        with engine.connect() as connection:
            assert "links" not in inspect(connection).get_table_names()
        migrate("upgrade", "head")
        with engine.connect() as connection:
            assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
    finally:
        engine.dispose()


@pytest.mark.parametrize("source", ["environment", "dotenv"])
def test_offline_migration_uses_configured_database_url(tmp_path, source):
    database_url = "postgresql+psycopg://example:p%40ss@database:5432/example"
    env = {key: value for key, value in os.environ.items() if key.upper() != "DATABASE_URL"}
    if source == "environment":
        env["DATABASE_URL"] = database_url
    else:
        (tmp_path / ".env").write_text(f"DATABASE_URL={database_url}\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(PROJECT_ROOT / "alembic.ini"),
            "upgrade",
            "head",
            "--sql",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert "CREATE TABLE links" in result.stdout
    assert "SERIAL" in result.stdout
