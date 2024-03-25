from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError


class BaseService:
    def __init__(self, session: AsyncSession, model: SQLModel):
        self.session = session
        self.model = model
        self.model_name = model.__name__

    async def delete(self, model_id: str | int):
        item = await self.session.get(self.model, model_id)  # type: ignore[arg-type, func-returns-value]
        if not item:
            err_msg = f"{self.model_name} with id {model_id} not found"
            raise NotFoundError(err_msg)
        await self.session.delete(item)
        await self.session.commit()

    async def count(self, column_name: str | None = None) -> int:
        if column_name:
            # returns only rows count where the value in specified column_name is not None
            query = select(func.count(getattr(self.model, column_name)))
        # when column_name is not given, returns all rows count in the table
        query = select(func.count()).select_from(self.model)  # type: ignore[arg-type]
        return (await self.session.exec(query)).one()
