from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app_sqlalchemy_v1.core.deps import UserServiceDep
from app_sqlalchemy_v1.core.exceptions import NotFoundError
from app_sqlalchemy_v1.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserRead],
)
async def get_users(
    user_service: UserServiceDep,
    skip: int = 0,
    # ! use new Annotated type hint to replace direct Query
    # https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#alternative-old-query-as-the-default-value
    # limit: int = Query(default=100, le=100),
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await user_service.get_many(skip, limit)

@router.get("/{user_id}")
async def get_user(user_service: UserServiceDep, user_id: str):
    try:
        return await user_service.get(user_id)
    except NotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex


@router.post("/")
async def create_user(user_service: UserServiceDep, user: UserCreate):
    return await user_service.create(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
)
async def update_user(user_service: UserServiceDep, user_id: str, new_data: UserUpdate):
    return await user_service.update(user_id, new_data)
