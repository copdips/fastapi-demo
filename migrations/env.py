import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

"""
# ! Import your SQLModel models here
# https://github.com/tiangolo/full-stack-fastapi-template/blob/master/backend/app/alembic/env.py#L21

whether import all the db models explicitly like this:

```python
    from app.models.db_models import *
    from sqlmodel import SQLModel
    target_metadata = SQLModel.metadata
```

whether import the SQLModel use in the file where the db models are defined,
which means not `from sqlmodel import SQLModel`, but `from app.models.db_models import SQLModel`:

```python
    from app.models.db_models import SQLModel
    target_metadata = SQLModel.metadata
```

! SQLModel.metadata = MetaData(naming_convention=db_naming_convention) is defined in db_models.py
alembic will get it, and do the necessary automatically
or set the naming convention in env.py itself, see:
https://alembic.sqlalchemy.org/en/latest/naming.html#integration-of-naming-conventions-into-operations-autogenerate
"""
from app.models.db_models import SQLModel

# ! import settings to set sqlalchemy.url
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
print(f"DB_HOST: {settings.db_settings.DB_HOST}/{settings.db_settings.DB_NAME}")
config.set_main_option("sqlalchemy.url", settings.db_settings.DB_CONN_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# ! Set your SQLModel metadata here
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
