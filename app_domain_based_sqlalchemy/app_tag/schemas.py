from app_domain_based_sqlalchemy.app_common.schemas import (
    BaseModel,
    BaseReadModel,
    ForbidExtraMixin,
)


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase, ForbidExtraMixin): ...


class TagRead(TagBase, BaseReadModel):
    id: str


class TagUpdate(BaseModel, ForbidExtraMixin):
    name: str | None = None
    teams_names: list[str] | None = None
