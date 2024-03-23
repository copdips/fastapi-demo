from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.deps import get_db_session, get_user_service
from app.db.models.user_composite_models import UserReadComposite
from app.db.models.user_models import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()
endpoint_name = "users"


@router.get("/{user_id}", summary="Get single user", response_model=UserReadComposite)
async def get_user(
    # the initial parameter `*,` to mark all the rest of the parameters as "keyword only",
    # which solves the problem of default value parameter is put before parameter with no default value.
    # ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/#use-the-dependency
    *,
    user_service: UserService = Depends(get_user_service),
    user_id: str,
):
    return await user_service.get(user_id)


@router.get("/", summary="Get users", response_model=list[UserReadComposite])
async def get_users(
    *,
    user_service: UserService = Depends(get_user_service),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    return await user_service.get_many(offset, limit)


@router.post(
    "/",
    summary="Create a new user",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,  # default success status code is 200
)
async def create_user(
    *,
    session: AsyncSession = Depends(get_db_session),
    user: UserCreate,
):
    user_service = UserService(session)
    return await user_service.create(user)


@router.patch(
    "/{user_id}",
    summary="Update a user",
    response_model=UserRead,
)
async def update_user(
    *,
    user_service: UserService = Depends(get_user_service),
    user_id: str,
    user_update: UserUpdate,
):
    return await user_service.update(user_id, user_update)


@router.delete("/{user_id}", summary="Delete a user")
async def delete_user(
    *,
    user_service: UserService = Depends(get_user_service),
    user_id: str,
):
    await user_service.delete(user_id)
