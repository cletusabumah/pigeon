from logging.config import fileConfig

import sqlalchemy as sa
from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from app.config import settings
from app.database import Base
from app.models import Event, Game, GameMove, Player, ScoresheetUpload  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _migration_url() -> str:
    """Alembic runs synchronously — translate async app URLs to sync drivers."""
    url = settings.database_url
    if url.startswith("postgresql+asyncpg"):
        return url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    if url.startswith("sqlite+aiosqlite"):
        return url.replace("sqlite+aiosqlite", "sqlite", 1)
    return url


def _compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    if context.dialect.name == "sqlite":
        if isinstance(inspected_type, sa.CHAR) and isinstance(metadata_type, sa.Uuid):
            return False
    if context.dialect.name == "postgresql":
        if metadata_column.name == "ocr_raw_json":
            if type(inspected_type).__name__ in {"JSON", "JSONB"}:
                return False
        inspected_enum = getattr(inspected_type, "name", None)
        metadata_enum = getattr(metadata_type, "name", None)
        if inspected_enum and metadata_enum and inspected_enum == metadata_enum:
            return False
    return None


def _configure_context(**kwargs):
    return context.configure(
        target_metadata=target_metadata,
        compare_type=_compare_type,
        compare_server_default=False,
        **kwargs,
    )


def run_migrations_offline() -> None:
    url = _migration_url()
    _configure_context(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    _configure_context(connection=connection)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_migration_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
