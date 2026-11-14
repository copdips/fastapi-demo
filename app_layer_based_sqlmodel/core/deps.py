import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

# from fastapi_dependency import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app_layer_based_sqlmodel.core.db import async_session_factory
from app_layer_based_sqlmodel.core.logging import get_logger
from app_layer_based_sqlmodel.services import TagService, TeamService, UserService
from app_layer_based_sqlmodel.services.email import EmailService
from app_layer_based_sqlmodel.services.task import TaskService


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    # No session.begin() here: the services commit explicitly, and a transaction
    # opened by begin() cannot be used again after an explicit commit()
    # ("Can't operate on closed transaction inside context manager").
    # Closing the session rolls back any uncommitted work on error.
    async with async_session_factory() as session:
        yield session


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[UserService]:
    yield UserService(session, logger)


async def get_tag_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[TagService]:
    yield TagService(session, logger)


async def get_team_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[TeamService]:
    yield TeamService(session, logger)


async def get_task_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[TaskService]:
    yield TaskService(session, logger)


async def get_email_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[EmailService]:
    yield EmailService(session, logger)


DBDep = Annotated[AsyncSession, Depends(get_db_session)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
