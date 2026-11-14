import sqlalchemy as sa
from sqlmodel import Field

from app_layer_based_sqlmodel.models.base import (
    BaseModel,
    BaseReadModel,
    ForbidExtraMixin,
)


class TeamBase(BaseModel):
    # column types mirror app_domain_based_sqlalchemy.app_team.models: one DB, one schema.
    name: str = Field(unique=True, index=True, sa_type=sa.String(100))
    headquarters: str = Field(sa_type=sa.String(200))


class TeamCreate(TeamBase, ForbidExtraMixin): ...


class TeamRead(TeamBase, BaseReadModel):
    id: str
    # created_at: datetime
    # updated_at: datetime | None


class TeamUpdate(BaseModel, ForbidExtraMixin):
    name: str | None = None
    headquarters: str | None = None
    # instead of UPDATING users and tags, better to use add/remove users/tags
    # for a better user experience
    # because
    users_names: list[str] | None = None
    tags_names: list[str] | None = None
