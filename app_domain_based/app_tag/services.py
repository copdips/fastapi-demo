import logging
from collections.abc import Sequence

from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app_domain_based.app_common.services import BaseService
from app_domain_based.app_tag.models import Tag
from app_domain_based.app_tag.schemas import TagCreate, TagUpdate
from app_domain_based.app_team.models import Team
from app_domain_based.core.exceptions import NotFoundError


class TagService(BaseService[Tag]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, Tag, logger)

    async def create(self, tag: TagCreate) -> Tag:
        db_tag = Tag.model_validate(tag)
        self.session.add(db_tag)
        await self.session.commit()
        return db_tag

    async def get(self, tag_id: str) -> Tag:
        return await self.get_by_id(
            tag_id,
            [Tag.teams],
        )

    async def get_many(
        self,
        offset: int = 0,
        limit: int = Query(default=100, le=100),
    ) -> Sequence[Tag]:
        query = select(Tag).options(selectinload(Tag.teams)).offset(offset).limit(limit)
        return (await self.session.exec(query)).all()

    async def update(self, tag_id: str, new_data: TagUpdate) -> Tag:
        tag = await self.get_by_id(tag_id, [Tag.teams])
        tag_data_dump = new_data.model_dump(exclude_unset=True)
        if "teams_names" in tag_data_dump:
            # set tag.teams to empty list to use tag.teams.extend() later as teams got from .all() is a Sequence type.
            # MyPy complains on `tag.teams = teams` but not `tag.teams.extend(teams)`
            # to use extend(), must pre-set tag.teams to empty list.
            tag.teams = []
            teams: Sequence[Team] = []
            if teams_names := set(tag_data_dump.pop("teams_names")):
                teams = (
                    await self.session.exec(
                        select(Team).where(
                            col(Team.name).in_(
                                teams_names,
                            ),
                        ),
                    )
                ).all()
                if len(teams) != len(teams_names):
                    msg = "Some teams not found."
                    raise NotFoundError(msg)
            tag.teams.extend(teams)
        tag.sqlmodel_update(tag_data_dump)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        tag.teams = await tag.awt_teams
        return tag
