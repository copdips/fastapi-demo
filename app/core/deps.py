from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_factory
from app.services import TagService, TeamService, UserService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[UserService, None]:
    yield UserService(session)


async def get_tag_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[TagService, None]:
    yield TagService(session)


async def get_team_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[TeamService, None]:
    yield TeamService(session)
