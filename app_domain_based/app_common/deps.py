import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

# from app_domain_based.services.email import EmailService
# from app_domain_based.services.task import TaskService
from app_domain_based.app_email.services import EmailService
from app_domain_based.app_task.services import TaskService
from app_domain_based.core.db import async_session_factory
from app_domain_based.core.logging import get_logger


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session, session.begin():
        try:
            yield session
        except Exception:
            # Any exception will trigger a rollback thanks to the explicit session.begin() context manager:
            # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#explicit-begin
            # Just re-raise to let FastAPI handle the error response
            raise


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
