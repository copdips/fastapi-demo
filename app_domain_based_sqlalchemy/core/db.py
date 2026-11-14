from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app_domain_based_sqlalchemy.app_common.models import Base
from app_domain_based_sqlalchemy.config import settings
from app_domain_based_sqlalchemy.core.init_db import create_init_data

# ref: https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html
if settings.testing:
    # debug("Using in-memory database.")
    sqlalchemy_db_url = "sqlite+aiosqlite:///"  # in-memory database
    # sqlalchemy_db_url = "sqlite+aiosqlite:///db.sqlite3"  # file-based database, but failed in integration test
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

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
)


async def create_db():
    # Base.metadata.create_all() receives only a sync engine, not async
    # use run_sync() to run the sync function
    # ref: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.drop_all,
        )


async def init_db(async_session_factory: async_sessionmaker[AsyncSession]):
    # ! when using multi worker with gunicorn or uvicorn, DB setup should be remove to outside of FastAPI
    # https://fastapi.tiangolo.com/deployment/docker/#multiple-containers
    await drop_db()
    await create_db()
    await create_init_data(async_session_factory)
