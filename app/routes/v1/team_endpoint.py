from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.deps import TeamServiceDep
from app.models.team_composite_models import (
    TeamReadComposite,
)
from app.models.team_models import TeamCreate, TeamRead, TeamUpdate

router = APIRouter()
endpoint_name = "teams"


@router.get(
    "/{team_id}",
    summary="Get single team",
    response_model=TeamReadComposite,
)
async def get_team(
    # the initial parameter `*,` to mark all the rest of the parameters as "keyword only",
    # which solves the problem of default value parameter is put before parameter with no default value.
    # ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/#use-the-dependency
    *,
    team_service: TeamServiceDep,
    team_id: str,
):
    return await team_service.get(team_id)


@router.get(
    "/",
    summary="Get teams",
    response_model=list[TeamReadComposite],
)
async def get_teams(
    *,
    team_service: TeamServiceDep,
    skip: int = 0,
    # ! use new Annotated type hint to replace direct Query
    # https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#alternative-old-query-as-the-default-value
    # limit: int = Query(default=100, le=100),
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await team_service.get_many(skip, limit)


@router.post(
    "/",
    summary="Create a new team",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    *,
    team_service: TeamServiceDep,
    team: TeamCreate,
):
    return await team_service.create(team)


@router.patch(
    "/{team_id}",
    summary="Update a team",
    response_model=TeamRead,
)
async def update_team(
    *,
    team_service: TeamServiceDep,
    team_id: str,
    team_update: TeamUpdate,
):
    return await team_service.update(team_id, team_update)


@router.delete(
    "/{team_id}",
    summary="Delete a team",
)
async def delete_team(
    *,
    team_service: TeamServiceDep,
    team_id: str,
):
    await team_service.delete(team_id)
