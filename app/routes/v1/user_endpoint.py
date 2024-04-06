from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Query, status

from app.core.deps import EmailServiceDep, UserServiceDep
from app.core.logging import get_logger
from app.models.user_composite_models import UserReadComposite
from app.models.user_models import UserCreate, UserRead, UserUpdate

router = APIRouter()
endpoint_name = "users"
logger = get_logger()


@router.get("/{user_id}", summary="Get single user", response_model=UserReadComposite)
async def get_user(
    # the initial parameter `*,` to mark all the rest of the parameters as "keyword only",
    # which solves the problem of default value parameter is put before parameter with no default value.
    # ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/#use-the-dependency
    *,
    user_service: UserServiceDep,
    user_id: str,
):
    logger.info("Getting single user")
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
    logger.info("Getting some users")
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
    response_model=UserReadComposite,
)
async def update_user(
    *,
    user_service: UserServiceDep,
    user_id: str,
    user_update: UserUpdate,
    email_service: EmailServiceDep,
    background_tasks: BackgroundTasks,
):
    user_before_update = await user_service.get(user_id)
    user = await user_service.update(user_id, user_update)
    background_tasks.add_task(
        email_service.send_for_user_update,
        user,
        user_update,
        user_before_update,
    )
    return user


@router.delete("/{user_id}", summary="Delete a user")
async def delete_user(
    *,
    user_service: UserServiceDep,
    user_id: str,
):
    await user_service.delete(user_id)
