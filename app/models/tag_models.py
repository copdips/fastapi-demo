from uuid import UUID

from pydantic import ConfigDict

from app.models.base_models import BaseModel, BaseReadModel, TagBase


class TagCreate(TagBase):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]
    # or:
    # class Config:
    #     extra = "forbid"


class TagRead(TagBase, BaseReadModel):
    id: UUID
    # created_at: datetime
    # updated_at: datetime | None


class TagUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]
    name: str | None = None
    teams_names: list[str] | None = None
