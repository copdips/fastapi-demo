from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.deps import UserServiceDep
from app.models.user_composite_models import UserReadComposite
from app.models.user_models import UserCreate, UserRead, UserUpdate

router = APIRouter()
endpoint_name = "users"


@router.get("/{user_id}", summary="Get single user", response_model=UserReadComposite)
async def get_user(
    # the initial parameter `*,` to mark all the rest of the parameters as "keyword only",
    # which solves the problem of default value parameter is put before parameter with no default value.
    # ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/#use-the-dependency
    *,
    user_service: UserServiceDep,
    user_id: UUID,
):
    return await user_service.get(user_id)


@router.get("/", summary="Get users", response_model=list[UserReadComposite])
async def get_users(
    *,
    user_service: UserServiceDep,
    skip: int = 0,
    # ! use new Annotated type hint to replace direct Query
    # https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#alternative-old-query-as-the-default-value
    # limit: int = Query(default=100, le=100),
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await user_service.get_many(skip, limit)


@router.post(
    "/",
    summary="Create a new user",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,  # default success status code is 200
)
async def create_user(
    *,
    user_service: UserServiceDep,
    user: UserCreate,
):
    return await user_service.create(user)


@router.patch(
    "/{user_id}",
    summary="Update a user",
    response_model=UserRead,
)
async def update_user(
    *,
    user_service: UserServiceDep,
    user_id: UUID,
    user_update: UserUpdate,
):
    return await user_service.update(user_id, user_update)


@router.delete("/{user_id}", summary="Delete a user")
async def delete_user(
    *,
    user_service: UserServiceDep,
    user_id: UUID,
):
    await user_service.delete(user_id)
