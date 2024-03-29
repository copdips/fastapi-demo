import logging
from typing import Any

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.db_models import BaseSQLModel


class BaseService:
    def __init__(
        self,
        session: AsyncSession,
        model: type[BaseSQLModel],
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
    ) -> type[BaseSQLModel]:
        try:
            query = select(  # pyright: ignore[reportCallIssue]
                self.model,  # pyright: ignore[reportArgumentType]
            )
            if selectin_attributes:
                for attr in selectin_attributes:
                    query = query.options(
                        selectinload(attr),
                    )
            query = query.where(self.model.id == model_id)
            item = (await self.session.exec(query)).one()
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
        query = select(func.count()).select_from(self.model)  # type: ignore[arg-type]
        return (await self.session.exec(query)).one()
