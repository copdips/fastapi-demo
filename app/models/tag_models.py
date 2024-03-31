from sqlmodel import Field

from app.models.base_models import BaseModel, BaseReadModel, ForbidExtraMixin


class TagBase(BaseModel):
    name: str = Field(unique=True, index=True)


class TagCreate(TagBase, ForbidExtraMixin): ...


class TagRead(TagBase, BaseReadModel):
    id: str
    # created_at: datetime
    # updated_at: datetime | None


class TagUpdate(BaseModel, ForbidExtraMixin):
    name: str | None = None
    teams_names: list[str] | None = None
