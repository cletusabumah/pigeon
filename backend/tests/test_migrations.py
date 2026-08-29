"""Alembic migration smoke tests — upgrade/downgrade on a temp database."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TABLES = {
    "alembic_version",
    "events",
    "players",
    "games",
    "game_moves",
    "scoresheet_uploads",
}


def _run_alembic(*args: str, database_url: str) -> None:
    env = {**os.environ, "DATABASE_URL": database_url}
    subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_ROOT,
        env=env,
        check=True,
    )


def _sqlite_tables(db_path: Path) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return {name for (name,) in rows}
    finally:
        conn.close()


def test_migrations_upgrade_downgrade_roundtrip_sqlite(tmp_path):
    db_path = tmp_path / "migrations_test.db"
    database_url = f"sqlite+aiosqlite:///{db_path}"

    _run_alembic("upgrade", "head", database_url=database_url)
    assert EXPECTED_TABLES.issubset(_sqlite_tables(db_path))

    _run_alembic("downgrade", "base", database_url=database_url)
    remaining = _sqlite_tables(db_path)
    assert "games" not in remaining
    assert "events" not in remaining

    _run_alembic("upgrade", "head", database_url=database_url)
    assert EXPECTED_TABLES.issubset(_sqlite_tables(db_path))


@pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_MIGRATION_TEST") != "1",
    reason="Set RUN_POSTGRES_MIGRATION_TEST=1 with DATABASE_URL pointing at Postgres",
)
def test_migrations_upgrade_downgrade_roundtrip_postgres():
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/chess_archive",
    )
    if not database_url.startswith("postgresql"):
        pytest.skip("DATABASE_URL is not PostgreSQL")

    _run_alembic("upgrade", "head", database_url=database_url)
    _run_alembic("downgrade", "base", database_url=database_url)
    _run_alembic("upgrade", "head", database_url=database_url)
