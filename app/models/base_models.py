import re
from enum import Enum

import sqlalchemy as sa
from pydantic import ConfigDict, computed_field
from pydantic.alias_generators import to_camel, to_snake
from sqlmodel import SQLModel

from app.settings import settings


class TaskStatus(Enum):
    in_progress = "in_progress"
    pending = "pending"
    done = "done"
    failed = "failed"


class BaseModel(SQLModel):
    @sa.orm.declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)

    if settings.use_camel_case:
        model_config = ConfigDict(  # type: ignore[assignment]
            alias_generator=to_camel,
            populate_by_name=True,  # Pydantic v1: allow_population_by_field_name=True
        )


class HateoasLink(BaseModel):
    href: str
    title: str


class HateoasLinks(BaseModel):
    self: HateoasLink


class HateoasModel(BaseModel):
    @computed_field
    def _links(self) -> HateoasLinks:
        # ! HATEOAS style, dynamic href generation is complex, here's more or less hardcoded.
        # ! api route version number is not included in the href, hard to get it.
        table_name = re.sub("Read.*", "", self.__class__.__name__).lower()
        # model name TeamRead will get teams as table_name,
        # model name TeamReadComposite will get teams as table_name too,
        # which means the model name should be well prepared.
        endpoint = f"{table_name}s"
        href = f"/{endpoint}/{self.id}"
        return HateoasLinks.model_validate(
            {
                "self": {"href": href, "title": table_name},
            },
        )


class BaseReadModel(HateoasModel): ...
