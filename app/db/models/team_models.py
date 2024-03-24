from pydantic import ConfigDict
from sqlmodel import SQLModel

from app.db.models.base_models import TeamBase


class TeamCreate(TeamBase):
    # https://docs.pydantic.dev/2.6/errors/validation_errors/#extra_forbidden
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]


class TeamRead(TeamBase):
    id: str
    # created_at: datetime
    # updated_at: datetime | None


class TeamUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]
    name: str | None = None
    headquarters: str | None = None
    # instead of UPDATING users and tags, better to use add/remove users/tags
    # for a better user experience
    # because
    users_names: list[str] | None = None
    tags_names: list[str] | None = None
