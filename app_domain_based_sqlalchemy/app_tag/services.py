import logging
from collections.abc import Sequence

from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_domain_based_sqlalchemy.app_common.services import BaseService
from app_domain_based_sqlalchemy.app_tag.models import Tag
from app_domain_based_sqlalchemy.app_tag.schemas import TagCreate, TagUpdate
from app_domain_based_sqlalchemy.app_team.models import Team
from app_domain_based_sqlalchemy.core.exceptions import NotFoundError


class TagService(BaseService[Tag]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, Tag, logger)

    async def create(self, tag: TagCreate) -> Tag:
        db_tag = Tag(**tag.model_dump())
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
        return (await self.session.execute(query)).scalars().all()

    async def update(self, tag_id: str, new_data: TagUpdate) -> Tag:
        tag = await self.get_by_id(tag_id, [Tag.teams])
        tag_data_dump = new_data.model_dump(exclude_unset=True)
        # ! query before assigning the relationship: assigning first marks the
        # previously associated rows as removed, and the autoflush before the
        # SELECT would delete/clear them.
        if "teams_names" in tag_data_dump:
            teams_names = set(tag_data_dump.pop("teams_names") or [])
            teams: Sequence[Team] = []
            if teams_names:
                teams = (
                    await self.session.execute(
                        select(Team).where(
                            Team.name.in_(
                                teams_names,
                            ),
                        ),
                    )
                ).scalars().all()
                if len(teams) != len(teams_names):
                    msg = "Some teams not found."
                    raise NotFoundError(msg)
            tag.teams = list(teams)
        for key, value in tag_data_dump.items():
            setattr(tag, key, value)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag, ["teams"])
        return tag
