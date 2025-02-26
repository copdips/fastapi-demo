import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app_domain_based.app_common.deps import get_db_session
from app_domain_based.app_task.services import TaskService
from app_domain_based.core.logging import get_logger


async def get_task_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[TaskService, None]:
    yield TaskService(session, logger)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
