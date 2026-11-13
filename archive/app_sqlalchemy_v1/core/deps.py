from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_sqlalchemy_v1.core.db import get_db_session
from app_sqlalchemy_v1.services.user import UserService

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


async def get_user_service(
    session: DBSessionDep,
) -> AsyncGenerator[UserService, None]:
    yield UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
# TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
# TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]
# TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
# EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
