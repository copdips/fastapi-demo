from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app_sqlachemy_v1.core.db import get_db_session
from app_sqlachemy_v1.models.tag import Tag

router = APIRouter()



@router.get("/")
async def get_tags(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(Tag))
    tags = result.scalars().all()
    return tags


@router.post("/")
async def create_tag(name: str, session: AsyncSession = Depends(get_db_session)):
    new_tag = Tag(name=name)
    session.add(new_tag)
    await session.commit()
    await session.refresh(new_tag)
    return new_tag
