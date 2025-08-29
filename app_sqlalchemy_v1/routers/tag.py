from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app_sqlalchemy_v1.core.db import get_db_session
from app_sqlalchemy_v1.models.tag import Tag

router = APIRouter()


@router.get("")
async def get_tags(session: Annotated[AsyncSession, Depends(get_db_session)]):
    result = await session.execute(select(Tag))
    return result.scalars().all()


@router.post("")
async def create_tag(
    name: str, session: Annotated[AsyncSession, Depends(get_db_session)]
):
    new_tag = Tag(name=name)
    session.add(new_tag)
    await session.commit()
    await session.refresh(new_tag)
    return new_tag
