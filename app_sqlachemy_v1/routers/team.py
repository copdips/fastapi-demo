from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # added import

from app_sqlachemy_v1.core.db import get_db_session
from app_sqlachemy_v1.models.team import Team

router = APIRouter()


@router.get("/")
async def get_teams(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(Team))
    teams = result.scalars().all()
    return teams


@router.get("/{team_id}")
async def get_team(team_id: int, session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(
        select(Team)
        .options(selectinload(Team.users))
        .where(Team.id == team_id)
    )
    team = result.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/")
async def create_team(name: str, session: AsyncSession = Depends(get_db_session)):
    new_team = Team(name=name)
    session.add(new_team)
    await session.commit()
    await session.refresh(new_team)
    return new_team
