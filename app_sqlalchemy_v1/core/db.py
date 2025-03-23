from collections.abc import AsyncGenerator, Callable

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app_sqlalchemy_v1.models.association import UserTagAssociation
from app_sqlalchemy_v1.models.base import Base
from app_sqlalchemy_v1.models.tag import Tag
from app_sqlalchemy_v1.models.team import Team
from app_sqlalchemy_v1.models.user import User

DATABASE_URL = "sqlite+aiosqlite:///./app_sqlalchemy_v1.sqlite3"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Verify connection is still active
    # Required for SQLite
    connect_args={"check_same_thread": False},
)

# DATABASE_URL = settings.db_settings.DB_CONN_URL
# engine = create_async_engine(
#     DATABASE_URL,
#     echo=True,
# )


async def create_init_data(async_session_factory: Callable[[], AsyncSession]):
    async with async_session_factory() as session:
        team_1 = Team(name="Team 1")
        team_2 = Team(name="Team 2")
        user_1 = User(name="user 1", team=team_1)
        user_2 = User(name="user 2", team=team_2)
        user_3 = User(name="user 3", team=team_2)
        tag_1 = Tag(name="tag 1", users=[user_1, user_2])
        tag_2 = Tag(name="tag 2", users=[user_2, user_3])
        session.add_all([team_1, team_2, user_1, user_2, user_3, tag_1, tag_2])
        await session.commit()


async def create_init_data_from_list(async_session_factory: Callable[[], AsyncSession]):
    async with async_session_factory() as session:
        # generate data in list of dict format, then bulk insert them with async session in sqlalchemy v1,4 syntax, with same data as create_init_data
        # Insert teams
        teams_data = [
            {"name": "Team 1"},
            {"name": "Team 2"},
        ]
        users_data = [
            {"name": "user 1", "team_name": "Team 1"},
            {"name": "user 2", "team_name": "Team 2"},
            {"name": "user 3", "team_name": "Team 2"},
        ]
        tags_data = [
            {"name": "tag 1"},
            {"name": "tag 2"},
        ]
        users_tags_data = [
            {"user_name": "user 1", "tag_name": "tag 1", "extra_data": "1_1"},
            {"user_name": "user 1", "tag_name": "tag 2", "extra_data": "1_2"},
            {"user_name": "user 2", "tag_name": "tag 1", "extra_data": "2_1"},
            {"user_name": "user 2", "tag_name": "tag 2", "extra_data": "2_2"},
            {"user_name": "user 3", "tag_name": "tag 2", "extra_data": "3_2"},
        ]

        # sqlalchemy async session does not support bulk_insert_mappings
        # await session.bulk_insert_mappings(Team, teams_data)
        await session.execute(insert(Team), teams_data)
        """
        # ! can also use:
        await async_session.run_sync(lambda session: session.bulk_insert_mappings(....))

        as zzzeek said:
        https://github.com/sqlalchemy/sqlalchemy/discussions/6935#discussioncomment-4789701

        First is, you can absolutely use the existing legacy bulk APIs with async. Just use session.run_sync , which is how the asyncsession runs everything anyway:

        Futhermore, sqlaclchemy v1.4 bulk_insert_mappings is less performant than v2
        """
        teams_db = (await session.execute(select(Team))).scalars().all()
        teams_mapping = {team.name: team.id for team in teams_db}

        # Update users_data to use team_id instead of team_name
        for user in users_data:
            user["team_id"] = teams_mapping[user.pop("team_name")]

        await session.execute(insert(User), users_data)
        users_db = (await session.execute(select(User))).scalars().all()
        users_mapping = {user.name: user.id for user in users_db}

        await session.execute(insert(Tag), tags_data)
        tags_db = (await session.execute(select(Tag))).scalars().all()
        tags_mapping = {tag.name: tag.id for tag in tags_db}

        # Update users_tags_data to use user_ids instead of user_names;
        # tag_ids instead of tag_names
        for user_tag in users_tags_data:
            user_tag["user_id"] = users_mapping[user_tag.pop("user_name")]
            user_tag["tag_id"] = tags_mapping[user_tag.pop("tag_name")]

        await session.execute(insert(UserTagAssociation), users_tags_data)
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
    # await create_init_data(async_session)
    await create_init_data_from_list(async_session)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session, session.begin():
        try:
            yield session
        except Exception:
            # Any exception will trigger a rollback thanks to the explicit session.begin() context manager:
            # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#explicit-begin
            # Just re-raise to let FastAPI handle the error response
            raise
