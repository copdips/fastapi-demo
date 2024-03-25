from collections.abc import Sequence

from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.db_models import Tag
from app.models.tag_models import TagCreate, TagUpdate
from app.models.team_models import TeamRead
from app.services.base_service import BaseService


class TagService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Tag)

    async def create(self, tag: TagCreate) -> Tag:
        db_tag = Tag.model_validate(tag)
        self.session.add(db_tag)
        await self.session.commit()
        return db_tag

    async def get(self, tag_id: str) -> Tag:
        tag = await self.session.get(Tag, tag_id, options=[selectinload(Tag.teams)])
        if not tag:
            err_msg = f"Tag with id {tag_id} not found"
            raise NotFoundError(err_msg)
        return tag

    async def get_many(
        self,
        offset: int = 0,
        limit: int = Query(default=100, le=100),
    ) -> Sequence[Tag]:
        query = select(Tag).options(selectinload(Tag.teams)).offset(offset).limit(limit)
        return (await self.session.exec(query)).all()

    async def update(self, tag_id: str, new_data: TagUpdate) -> Tag:
        tag = await self.session.get(Tag, tag_id, options=[selectinload(Tag.teams)])
        if not tag:
            err_msg = f"Tag with id {tag_id} not found"
            raise NotFoundError(err_msg)
        tag_data_dump = new_data.model_dump(exclude_unset=True)
        if "teams_names" in tag_data_dump:
            if teams_names := set(tag_data_dump.pop("teams_names")):
                teams = (
                    await self.session.exec(
                        select(TeamRead).where(TeamRead.name.in_(teams_names)),
                    )
                ).all()
                if len(teams) != len(teams_names):
                    msg = "Some teams not found."
                    raise NotFoundError(msg)
            else:
                teams = []
            tag.teams = teams
        tag.sqlmodel_update(tag_data_dump)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag
