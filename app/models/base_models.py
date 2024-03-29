import re
from datetime import UTC, datetime
from enum import Enum

import shortuuid
import sqlalchemy as sa
from pydantic import ConfigDict, computed_field
from pydantic.alias_generators import to_camel, to_snake
from sqlmodel import Field, SQLModel
from ulid import ULID

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


class BaseSQLModel(BaseModel):
    # ! validate_assignment=True to validate during SALModel(table=True) instance creation
    # https://github.com/tiangolo/sqlmodel/issues/52#issuecomment-1998440311
    model_config = ConfigDict(validate_assignment=True)

    # ! if uid and id are computed at SQL level, we should add `| None` on the typing,
    # and add `default=None` in the Field.
    # Here both of uid and id columns are computed at python level, so no need to add `| None`
    # ref: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#primary-key-id
    uid: str = Field(default_factory=lambda: str(ULID()), primary_key=True)
    id: str = Field(
        default_factory=shortuuid.uuid,
        index=True,
        nullable=False,
        unique=True,
    )
    created_at: datetime = Field(
        sa_type=sa.DateTime(timezone=True),
        default_factory=lambda: datetime.now(UTC),
        # or without lambda, but using datetime.utcnow throws deprecation error.
        # default_factory=datetime.utcnow,
        # ! dont use default=datetime.utcnow() as it applies the same datetime to all rows.
        # ! https://docs.pydantic.dev/latest/concepts/models/#fields-with-dynamic-default-values
        # default=datetime.utcnow(),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate": sa.func.now(),
            # ! should be callable if use pure python method, and should not be datetime.utcnow, as utc will be applied twice, once by utcnow, once by sa.DateTime(timezone=True)
            # "onupdate": datetime.now,
        },
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
