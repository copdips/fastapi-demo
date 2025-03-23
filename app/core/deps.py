import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_factory
from app.core.logging import get_logger
from app.services import TagService, TeamService, UserService
from app.services.email import EmailService
from app.services.task import TaskService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    # # Using begin() context manager automatically handles commit/rollback
    async with async_session_factory() as session, session.begin():
        try:
            yield session
        except Exception:
            # Any exception will trigger a rollback thanks to the explicit session.begin() context manager:
            # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#explicit-begin
            # Just re-raise to let FastAPI handle the error response
            raise


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[UserService, None]:
    yield UserService(session, logger)


async def get_tag_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[TagService, None]:
    yield TagService(session, logger)


async def get_team_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[TeamService, None]:
    yield TeamService(session, logger)


async def get_task_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[TaskService, None]:
    yield TaskService(session, logger)


async def get_email_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[EmailService, None]:
    yield EmailService(session, logger)


DBDep = Annotated[AsyncSession, Depends(get_db_session)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
