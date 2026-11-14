from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_domain_based_sqlalchemy.core.db import async_session_factory

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    # No session.begin() here: the services commit explicitly, and a transaction
    # opened by begin() cannot be used again after an explicit commit()
    # ("Can't operate on closed transaction inside context manager").
    # Closing the session rolls back any uncommitted work on error.
    async with async_session_factory() as session:
        yield session


DBDep = Annotated[AsyncSession, Depends(get_db_session)]
