from datetime import UTC, datetime

import shortuuid
import sqlalchemy as sa
from pydantic import ConfigDict
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, MetaData, SQLModel
from ulid import ULID

from app_domain_based.app_common.schemas import BaseModel

# declare SQLModel here to be used in alembic migrations/env.py to avoid MyPy error
__all__ = ["SQLModel"]

# https://medium.com/@chjiang15/dont-forget-your-naming-constraints-sqlalchemy-alembic-top-tip-89022a54a4b0
db_naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.MetaData.params.naming_convention
    # https://docs.sqlalchemy.org/en/20/core/constraints.html#constraint-naming-conventions
    # ! if constraint_name doesn't work use: "ck": "ck_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
SQLModel.metadata = MetaData(naming_convention=db_naming_convention)


class BaseSQLModel(
    BaseModel,
    AsyncAttrs,
):
    # ! validate_assignment=True to validate during SALModel(table=True) instance creation
    # https://github.com/tiangolo/sqlmodel/issues/52#issuecomment-1998440311
    model_config = ConfigDict(
        validate_assignment=True,
    )  # pyright: ignore[reportAssignmentType]

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
        # default vs default_factory:
        # ! default_factory is introduced in sqlalchemy v2
        # https://github.com/sqlalchemy/sqlalchemy/discussions/11372#discussioncomment-9370737
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
            # if relationship changes, for e.g. set one more user in a team
            # the updated_at won't be updated automatically
            "onupdate": sa.func.now(),
            # ! should be callable if use pure python method, and should not be datetime.utcnow, as utc will be applied twice, once by utcnow, once by sa.DateTime(timezone=True)
            # "onupdate": datetime.now,
        },
    )
