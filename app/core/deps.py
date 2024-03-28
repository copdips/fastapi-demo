from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_factory
from app.services import TagService, TeamService, UserService
from app.services.task_service import TaskService


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


async def get_task_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[TaskService, None]:
    yield TaskService(session)


DBDep = Annotated[AsyncSession, Depends(get_db_session)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]
TaskServiceDep = Annotated[TeamService, Depends(get_task_service)]
