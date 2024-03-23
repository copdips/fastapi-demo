from collections.abc import Sequence

from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.db_models import User
from app.db.models.user_models import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserCreate) -> User:
        db_user = User.model_validate(user)
        self.session.add(db_user)
        await self.session.commit()
        return db_user

    async def get(self, user_id: str) -> User:
        # selectinload(User.team) for eager loading
        user = await self.session.get(User, user_id, options=[selectinload(User.team)])
        # user is None or a type of user_model.User
        # if user does not exist, user is None, no exception raised
        if not user:
            err_msg = f"User with id {user_id} not found"
            raise NotFoundError(err_msg)
        return user

    async def get_many(
        self,
        offset: int = 0,
        limit: int = Query(default=100, le=100),
    ) -> Sequence[User]:  # List[Union[User, Team]
        # query = select(User, Team).where(User.team_id == Team.id) # inner join
        # query = select(User).join(Team)  # inner join with User data only
        # query = select(User, Team).join(Team)  # inner join with both User and Team
        # query = select(User, Team).join(Team, isouter=True)  # left join
        query = (
            select(User).options(selectinload(User.team)).offset(offset).limit(limit)
        )
        return (await self.session.exec(query)).all()
        # for user, team in res:
        # debug("=====================================")
        # debug(f"user_1: {user_1}")
        # debug("user:", user, "Team:", team)
        # breakpoint()

    async def update(self, user_id: str, new_data: UserUpdate) -> User:
        user = await self.session.get(User, user_id)
        if not user:
            err_msg = f"User with id {user_id} not found"
            raise NotFoundError(err_msg)
        # exclude_unset=True is important, as it will not update fields with unset value.
        # it's very powerful where if client intentionally set a field to None,
        # it won't consider it as unset.
        # ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/#remove-fields
        user_data_dump = new_data.model_dump(exclude_unset=True)
        user.sqlmodel_update(user_data_dump)
        self.session.add(user)
        await self.session.commit()
        # right after session.commit(), user object is no more accessible,
        # so we need to refresh it, and also get update_at field updated.
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: str):
        user = await self.session.get(User, user_id)
        if not user:
            err_msg = f"User with id {user_id} not found"
            raise NotFoundError(err_msg)
        await self.session.delete(user)
        await self.session.commit()
