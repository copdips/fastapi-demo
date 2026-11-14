import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# from app_domain_based_sqlalchemy.services.email import EmailService
# from app_domain_based_sqlalchemy.services.task import TaskService
from app_domain_based_sqlalchemy.app_email.services import EmailService
from app_domain_based_sqlalchemy.app_task.services import TaskService
from app_domain_based_sqlalchemy.core.db import async_session_factory
from app_domain_based_sqlalchemy.core.logging import get_logger


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    # No session.begin() here: the services commit explicitly, and a transaction
    # opened by begin() cannot be used again after an explicit commit()
    # ("Can't operate on closed transaction inside context manager").
    # Closing the session rolls back any uncommitted work on error.
    async with async_session_factory() as session:
        yield session


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
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
