from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app_sqlachemy_v1.core.db import get_db_session
from app_sqlachemy_v1.models.tag import Tag
from app_sqlachemy_v1.models.user import User

router = APIRouter()


@router.get("/")
async def get_users(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


@router.post("/")
async def create_user(
    name: str, team_id: int, session: AsyncSession = Depends(get_db_session)
):
    new_user = User(name=name, team_id=team_id)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post("/{user_id}/tags/{tag_id}")
async def assign_tag(
    user_id: int, tag_id: int, session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await session.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    user.tags.append(tag)
    await session.commit()
    return {"msg": "Tag assigned to user"}
