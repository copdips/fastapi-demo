from sqlmodel import Field

from app.models.base_models import BaseModel, BaseReadModel, ForbidExtraMixin


class TeamBase(BaseModel):
    name: str = Field(unique=True, index=True)
    headquarters: str


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
