from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel

from app.db.models.base_models import TagBase


class TagCreate(TagBase):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]
    # or:
    # class Config:
    #     extra = "forbid"


class TagRead(TagBase):
    id: str
    created_at: datetime
    updated_at: datetime | None


class TagUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]
    name: str | None = None
    teams_names: list[str] | None = None
