from collections.abc import Sequence

from fastapi import Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app_sqlalchemy_v1.core.exceptions import NotFoundError
from app_sqlalchemy_v1.models import Team, User
from app_sqlalchemy_v1.models.association import UserTagAssociation
from app_sqlalchemy_v1.schemas.user import UserCreate, UserUpdate
from app_sqlalchemy_v1.services.base import BaseService


class UserService(BaseService[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def create(self, user: UserCreate) -> User:
        db_user = User(**user.model_dump())  # Pydantic v1: User.from_orm(user)
        self.session.add(db_user)
        await self.session.commit()
        return db_user

    async def get(self, user_id: str) -> User:
        # selectinload(User.team) for eager loading
        return await self.get_by_id(
            user_id,
            [
                User.team,
                [User.tags, UserTagAssociation.tag],
            ],
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
            select(User).options(selectinload(User.team)).offset(offset).limit(limit)
        )

        # breakpoint()
        return (await self.session.execute(query)).scalars().all()
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
                await self.session.execute(
                    select(Team).where(Team.name == team_name),
                )
            ).one()
            user.team_id = team.id
        for field, value in user_data_dump.items():
            setattr(user, field, value)
        await self.session.commit()
        # right after session.commit(), user object is no more accessible,
        # so we need to refresh it, and also get update_at field updated.
        await self.session.refresh(user)
        user.team = await user.awt_team
        return user
