import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ! The domain-based layout is the canonical schema: it is what the Docker image
# ! deploys, and the two layouts describe the same tables (tests/integration/
# ! test_schema_parity.py keeps them in sync).
# ! Importing the model modules registers their tables on Base.metadata.
import app_domain_based_sqlalchemy.app_email.models  # noqa: F401
import app_domain_based_sqlalchemy.app_tag.models  # noqa: F401
import app_domain_based_sqlalchemy.app_task.models  # noqa: F401
import app_domain_based_sqlalchemy.app_team.models  # noqa: F401
import app_domain_based_sqlalchemy.app_user.models  # noqa: F401
from app_domain_based_sqlalchemy.app_common.models import Base
from app_domain_based_sqlalchemy.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
print(f"DB_HOST: {settings.db_settings.DB_HOST}/{settings.db_settings.DB_NAME}")
config.set_main_option("sqlalchemy.url", settings.db_settings.DB_CONN_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ! the naming convention and the table names come from Base (app_common/models.py).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
