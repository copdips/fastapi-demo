import logging
from collections.abc import Sequence

from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.db_models import Team, User
from app.models.user_models import UserCreate, UserUpdate
from app.services.base_service import BaseService


class UserService(BaseService[User]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, User, logger)

    async def create(self, user: UserCreate) -> User:
        db_user = User.model_validate(user)  # Pydantic v1: User.from_orm(user)
        self.session.add(db_user)
        await self.session.commit()
        return db_user

    async def get(self, user_id: str) -> User:
        # selectinload(User.team) for eager loading
        return await self.get_by_id(
            user_id,
            [User.team],
        )

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
            select(User)
            .options(selectinload(User.team))  # pyright: ignore[reportArgumentType]
            .offset(offset)
            .limit(limit)
        )
        return (await self.session.exec(query)).all()
        # for user, team in res:
        # debug(f"user_1: {user_1}")
        # debug("user:", user, "Team:", team)
        # breakpoint()

    async def update(self, user_id: str, new_data: UserUpdate) -> User:
        user: User = await self.get_by_id(user_id)
        if not user:
            err_msg = f"User with id {user_id} not found"
            raise NotFoundError(err_msg)
        # exclude_unset=True is important, as it will not update fields with unset value.
        # it's very powerful where if client intentionally set a field to None,
        # it won't consider it as unset.
        # ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/#remove-fields
        user_data_dump = new_data.model_dump(exclude_unset=True)
        if team_name := user_data_dump.pop("team_name", None):
            team = (
                await self.session.exec(
                    select(Team).where(Team.name == team_name),
                )
            ).one()
            user.team_id = team.id
        user.sqlmodel_update(user_data_dump)
        self.session.add(user)
        await self.session.commit()
        # right after session.commit(), user object is no more accessible,
        # so we need to refresh it, and also get update_at field updated.
        await self.session.refresh(user)
        user.team = await user.awt_team
        return user
