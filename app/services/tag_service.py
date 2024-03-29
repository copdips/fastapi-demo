from collections.abc import Sequence

from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.db_models import Tag, Team
from app.models.tag_models import TagCreate, TagUpdate
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
        return await self.get_by_id(
            tag_id,
            [Tag.teams],
        )  # pyright: ignore[reportReturnType]

    async def get_many(
        self,
        offset: int = 0,
        limit: int = Query(default=100, le=100),
    ) -> Sequence[Tag]:
        query = (
            select(Tag)
            .options(selectinload(Tag.teams))  # pyright: ignore[reportArgumentType]
            .offset(offset)
            .limit(limit)
        )
        return (await self.session.exec(query)).all()

    async def update(self, tag_id: str, new_data: TagUpdate) -> Tag:
        tag = await self.get_by_id(tag_id, [Tag.teams])
        tag_data_dump = new_data.model_dump(exclude_unset=True)
        if "teams_names" in tag_data_dump:
            if teams_names := set(tag_data_dump.pop("teams_names")):
                teams = (
                    await self.session.exec(
                        select(Team).where(
                            Team.name.in_(  # pyright: ignore[reportAttributeAccessIssue]
                                teams_names,
                            ),
                        ),
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
        return tag  # pyright: ignore[reportReturnType]
