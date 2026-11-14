import sqlalchemy as sa
from sqlmodel import Field

from app_layer_based_sqlmodel.models.base import (
    BaseModel,
    BaseReadModel,
    ForbidExtraMixin,
)


class TagBase(BaseModel):
    # column type mirrors app_domain_based_sqlalchemy.app_tag.models: one DB, one schema.
    name: str = Field(unique=True, index=True, sa_type=sa.String(100))


class TagCreate(TagBase, ForbidExtraMixin): ...


class TagRead(TagBase, BaseReadModel):
    id: str
    # created_at: datetime
    # updated_at: datetime | None


class TagUpdate(BaseModel, ForbidExtraMixin):
    name: str | None = None
    teams_names: list[str] | None = None
