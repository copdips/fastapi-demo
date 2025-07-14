from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app_sqlalchemy_v1.core.exceptions import NotFoundError
from app_sqlalchemy_v1.models.base import BaseMixin


class BaseService[T: BaseMixin]:
    """
    The above syntax is for Python 3.12 and later only.
    For earlier versions, use the following syntax:
    https://mypy.readthedocs.io/en/stable/generics.html#type-variables-with-upper-bounds

        from typing import Generic, TypeVar

        T = TypeVar("T", bound=BaseSQLModel)
        class BaseService(Generic[T]):
            ...

    """

    def __init__(
        self,
        session: AsyncSession,
        model: type[T],
    ):
        self.session = session
        self.model = model
        self.model_name = model.__name__

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
                    if isinstance(attr, list):
                        """
                        The loader options can also be "chained" using method chaining to specify how loading should occur further levels deep:

                        - https://docs.sqlalchemy.org/en/latest/orm/queryguide/relationships.html#relationship-loading-with-loader-options

                        - https://stackoverflow.com/a/32992858

                        chained selectinload (multiple selectinload in one options)
                        often used for nested many-ton-many relationships:

                        .options(
                            selectinload(User.tags)
                            .selectinload(UserTagAssociation.tag)
                        )

                        if we dont use chained selectinload, and use like this:

                        .options(selectinload(User.tags))
                        .options(selectinload(UserTagAssociation.tag))

                        we will get error:

                        sqlalchemy.exc.ArgumentError: Mapped attribute "UserTagAssociation.tag" does not apply to any of the root entities in this query, e.g. mapped class User->user. Please specify the full path from one of the root entities to the target attribute
                        """
                        chain = selectinload(attr[0])
                        for attr_in_attr in attr[1:]:
                            chain = chain.selectinload(attr_in_attr)
                        query = query.options(chain)
                    else:
                        # root level selectinload, for one-to-many or many-to-one relationships:
                        # .options(selectinload(User.team)).options(selectinload(User.team))
                        query = query.options(selectinload(attr))
            query = query.where(self.model.id == model_id)
            item = (await self.session.execute(query)).scalar_one()
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
        return (await self.session.execute(query)).one()
