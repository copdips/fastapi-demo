import logging
from collections.abc import Sequence

from fastapi import Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app_domain_based_sqlalchemy.app_common.services import BaseService
from app_domain_based_sqlalchemy.app_team.models import Team
from app_domain_based_sqlalchemy.app_user.models import User
from app_domain_based_sqlalchemy.app_user.schemas import UserCreate, UserUpdate
from app_domain_based_sqlalchemy.core.exceptions import NotFoundError


class UserService(BaseService[User]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, User, logger)

    async def create(self, user: UserCreate) -> User:
        db_user = User(**user.model_dump())
        self.session.add(db_user)
        await self.session.commit()
        return db_user

    async def get(self, user_id: str) -> User:
        # selectinload(User.team) for eager loading
        self.logger.info("Getting single user in service")
        return await self.get_by_id(
            user_id,
            [User.team],
        )

    async def get_many(
        self,
        offset: int = 0,
        limit: int = Query(default=100, le=100),
    ) -> Sequence[User]:
        query = (
            select(User).options(selectinload(User.team)).offset(offset).limit(limit)
        )
        self.logger.info("Getting some users in service")
        return (await self.session.execute(query)).scalars().all()

    async def update(self, user_id: str, new_data: UserUpdate) -> User:
        user: User = await self.get_by_id(user_id)
        if not user:
            err_msg = f"User with id {user_id} not found"
            raise NotFoundError(err_msg)
        # exclude_unset=True is important, as it will not update fields with unset value.
        # it's very powerful where if client intentionally set a field to None,
        # it won't consider it as unset.
        user_data_dump = new_data.model_dump(exclude_unset=True)
        if team_name := user_data_dump.pop("team_name", None):
            team = (
                await self.session.execute(
                    select(Team).where(Team.name == team_name),
                )
            ).scalars().one()
            user.team_id = team.id
        for key, value in user_data_dump.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        # right after session.commit(), the relationship is expired, so reload it
        # together with the updated_at column.
        await self.session.refresh(user, ["team"])
        return user
