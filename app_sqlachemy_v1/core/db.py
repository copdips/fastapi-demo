from typing import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from app_sqlachemy_v1.models.base import Base
from app_sqlachemy_v1.models.tag import Tag
from app_sqlachemy_v1.models.team import Team
from app_sqlachemy_v1.models.user import User

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    # Required for SQLite
    connect_args={"check_same_thread": False},
)


async def create_init_data(async_session_factory: Callable[[], AsyncSession]):
    async with async_session_factory() as session:
        # Team A and associated users
        team = Team(name="Team A")
        user = User(name="alice", team=team)
        tag = Tag(name="urgent")
        # Relationship: assign tag to user
        user.tags = [tag]
        # Additional user in Team A
        user_a2 = User(name="anna", team=team)
        # Team B and associated users
        team2 = Team(name="Team B")
        user2 = User(name="bob", team=team2)
        tag2 = Tag(name="info")
        # Relationship: assign tag2 to user2
        user2.tags = [tag2]
        # Additional user in Team B
        user_b2 = User(name="charlie", team=team2)
        # Combine and add all rows
        session.add_all([team, user, tag, user_a2, team2, user2, tag2, user_b2])
        await session.commit()


async def create_db():
    # SQLModel.metadata.create_all(engine) receives only a sync engine, not async
    # use run_sync() to run the sync function
    # ref: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.drop_all,
        )


async def init_db():
    await drop_db()
    await create_db()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    await create_init_data(async_session)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
