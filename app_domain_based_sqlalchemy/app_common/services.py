import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app_domain_based_sqlalchemy.app_common.models import Base
from app_domain_based_sqlalchemy.core.exceptions import NotFoundError


class BaseService[T: Base]:
    """
    The above syntax is for Python 3.12 and later only.
    For earlier versions, use the following syntax:
    https://mypy.readthedocs.io/en/stable/generics.html#type-variables-with-upper-bounds

        from typing import Generic, TypeVar

        T = TypeVar("T", bound=Base)
        class BaseService(Generic[T]):
            ...

    """

    def __init__(
        self,
        session: AsyncSession,
        # Specify that model is of type T, as model will be injected by sub class dynamically
        model: type[T],
        logger: logging.Logger,
    ):
        self.session = session
        self.model = model
        self.model_name = model.__name__
        self.logger = logger

    async def get_by_id(
        self,
        model_id: str,  # ! this is the id column, not the uid PK column
        selectin_attributes: list[Any] | None = None,
    ) -> T:  # Indicate that the return type is an instance of T, later we create sub class of BaseService with User as T: class UserService(BaseService[User])
        try:
            query = select(
                self.model,
            )
            if selectin_attributes:
                for attr in selectin_attributes:
                    query = query.options(
                        selectinload(attr),
                    )
            query = query.where(self.model.id == model_id)
            item = (await self.session.execute(query)).scalars().one()
        except NoResultFound as ex:
            err_msg = f"{self.model_name} with id {model_id} not found"
            raise NotFoundError(err_msg) from ex
        else:
            return item

    async def delete(self, model_id: str):
        item = await self.get_by_id(model_id)
        await self.session.delete(item)
        await self.session.commit()

    async def count(self, column_name: str | None = None) -> int:
        if column_name:
            # returns only rows count where the value in specified column_name is not None
            query = select(func.count(getattr(self.model, column_name)))
        # when column_name is not given, returns all rows count in the table
        query = select(func.count()).select_from(self.model)
        return (await self.session.execute(query)).scalars().one()
