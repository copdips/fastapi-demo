from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.config import settings
from app.models.init_db import create_init_data

"""
https://github.com/tiangolo/sqlmodel/blob/4c3f242ae215b28ef7b1dcb37411531999826d0d/sqlmodel/ext/asyncio/session.py#L99

The original SQLAlchemy `session.execute()` method that returns objects
of type `Row`, and that you have to call `scalars()` to get the model objects.

For example:

```Python
# sqlalchemy AsyncSession
heroes = await session.execute(select(Hero)).scalars().all()
```

instead, with sqlmodel's AsyncSession you could use `exec()`:

```Python
# sqlmodel AsyncSession
heroes = await session.exec(select(Hero)).all()
```
"""
# if use native sa's AsyncSession: from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession  # noqa: E402

if settings.testing:
    # debug("Using in-memory database.")
    sqlalchemy_db_url = "sqlite+aiosqlite:///"  # in-memory database
    # sqlalchemy_db_url = "sqlite+aiosqlite:///db.sqlite3"  # file-based database, but failed in integration test
    # https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#configure-the-in-memory-database
    engine = create_async_engine(
        sqlalchemy_db_url,
        echo=settings.debug,
        pool_pre_ping=True,  # Verify connection is still active
        connect_args={"check_same_thread": False},
        # sqlite pool class could be set automatically by SQLAlchemy
        # https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#threading-pooling-behavior
        # ! SqlAlchemy uses StaticPool by default when using a Memory Database in Multiple Threads
        # https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
        # poolclass=StaticPool,
    )
else:
    # debug("Using PG database.")
    db_settings = settings.db_settings
    sqlalchemy_db_url = f"postgresql+asyncpg://{db_settings.DB_USERNAME}:{db_settings.DB_PASSWORD}@{db_settings.DB_HOST}:{db_settings.DB_PORT}/{db_settings.DB_NAME}"
    # ! traditional QueuePool is not asyncio compatible
    # AsyncAdaptedQueuePool is used instead, and set automatically when using create_async_engine
    # https://docs.sqlalchemy.org/en/20/core/pooling.html#connection-pool-configuration
    engine = create_async_engine(
        sqlalchemy_db_url,
        echo=settings.debug,
        pool_pre_ping=True,  # Verify connection is still active
        pool_size=10,  # Adjust based on expected concurrent requests
        max_overflow=20,
    )

async_session_factory: type[AsyncSession] = async_sessionmaker(  # type: ignore[assignment]
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
)


async def create_db():
    # SQLModel.metadata.create_all(engine) receives only a sync engine, not async
    # use run_sync() to run the sync function
    # ref: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            SQLModel.metadata.drop_all,
        )


async def init_db(async_session_factory: type[AsyncSession]):
    # ! when using multi worker with gunicorn or uvicorn, DB setup should be remove to outside of FastAPI
    # https://fastapi.tiangolo.com/deployment/docker/#multiple-containers
    await drop_db()
    await create_db()
    await create_init_data(async_session_factory)
