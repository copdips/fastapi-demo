from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import Field

from app.models.base_models import BaseModel, BaseReadModel


class TeamBase(BaseModel):
    name: str = Field(unique=True, index=True)
    headquarters: str


class TeamCreate(TeamBase):
    # https://docs.pydantic.dev/2.6/errors/validation_errors/#extra_forbidden
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]


class TeamRead(TeamBase, BaseReadModel):
    id: UUID
    # created_at: datetime
    # updated_at: datetime | None


class TeamUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]
    name: str | None = None
    headquarters: str | None = None
    # instead of UPDATING users and tags, better to use add/remove users/tags
    # for a better user experience
    # because
    users_names: list[str] | None = None
    tags_names: list[str] | None = None
