from fastapi import APIRouter, Depends, Query, status

from app.core.deps import get_tag_service
from app.db.models.tag_composite_models import (
    TagReadComposite,
)
from app.db.models.tag_models import TagCreate, TagRead, TagUpdate
from app.services.tag_service import TagService

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
    tag_service: TagService = Depends(get_tag_service),
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
    tag_service: TagService = Depends(get_tag_service),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    return await tag_service.get_many(offset, limit)


@router.post(
    "/",
    summary="Create a new tag",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    *,
    tag_service: TagService = Depends(get_tag_service),
    tag: TagCreate,
):
    return await tag_service.create(tag)


@router.patch(
    "/{tag_id}",
    summary="Update a tag",
    response_model=TagRead,
)
async def update_tag(
    *,
    tag_service: TagService = Depends(get_tag_service),
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
    tag_service: TagService = Depends(get_tag_service),
    tag_id: str,
):
    await tag_service.delete(tag_id)
