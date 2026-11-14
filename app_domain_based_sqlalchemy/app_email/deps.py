from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app_domain_based_sqlalchemy.app_common.deps import get_db_session
from app_domain_based_sqlalchemy.app_email.services import EmailService
from app_domain_based_sqlalchemy.core.logging import get_logger

if TYPE_CHECKING:
    import logging
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def get_email_service(
    session: AsyncSession = Depends(get_db_session),
    logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[EmailService]:
    yield EmailService(session, logger)


EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
