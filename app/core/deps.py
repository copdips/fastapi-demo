from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_factory
from app.services import TagService, TeamService, UserService


async def get_db_session():
    async with async_session_factory() as session:
        yield session


async def get_user_service(session: AsyncSession = Depends(get_db_session)):
    yield UserService(session)


async def get_tag_service(session: AsyncSession = Depends(get_db_session)):
    yield TagService(session)


async def get_team_service(session: AsyncSession = Depends(get_db_session)):
    yield TeamService(session)
