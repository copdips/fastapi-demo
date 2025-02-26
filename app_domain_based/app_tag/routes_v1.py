from typing import Annotated

from fastapi import APIRouter, Query, status

from app_domain_based.app_tag.deps import TagServiceDep
from app_domain_based.app_tag.schemas import TagCreate, TagRead, TagUpdate
from app_domain_based.schema_composites.schema_composites import TagReadComposite

router = APIRouter()
endpoint_name = "tags"


@router.get(
    "/{tag_id}",
    summary="Get single tag",
    response_model=TagReadComposite,
)
async def get_tag(
    # the initial parameter `*,` to mark all the rest of the parameters as "keyword only",
    # which solves the problem of default value parameter is put before parameter with no default value.
    # ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/#use-the-dependency
    *,
    tag_service: TagServiceDep,
    tag_id: str,
):
    return await tag_service.get(tag_id)


@router.get(
    "/",
    summary="Get tags",
    response_model=list[TagReadComposite],
)
async def get_tags(
    *,
    tag_service: TagServiceDep,
    skip: int = 0,
    # ! use new Annotated type hint to replace direct Query
    # https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#alternative-old-query-as-the-default-value
    # limit: int = Query(default=100, le=100),
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await tag_service.get_many(skip, limit)


@router.post(
    "/",
    summary="Create a new tag",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    *,
    tag_service: TagServiceDep,
    tag: TagCreate,
):
    return await tag_service.create(tag)


@router.patch(
    "/{tag_id}",
    summary="Update a tag",
    response_model=TagReadComposite,
)
async def update_tag(
    *,
    tag_service: TagServiceDep,
    tag_id: str,
    tag_update: TagUpdate,
):
    return await tag_service.update(tag_id, tag_update)


@router.delete(
    "/{tag_id}",
    summary="Delete a tag",
)
async def delete_tag(
    *,
    tag_service: TagServiceDep,
    tag_id: str,
):
    await tag_service.delete(tag_id)
