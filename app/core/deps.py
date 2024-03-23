from app.db import async_session_factory
from app.services import TagService, TeamService, UserService


async def get_db_session():
    async with async_session_factory() as session:
        yield session


async def get_user_service():
    # async with async_session() as session, session.begin():
    async with async_session_factory() as session:
        yield UserService(session)


async def get_tag_service():
    # async with async_session() as session, session.begin():
    async with async_session_factory() as session:
        yield TagService(session)


async def get_team_service():
    # async with async_session() as session, session.begin():
    async with async_session_factory() as session:
        yield TeamService(session)
