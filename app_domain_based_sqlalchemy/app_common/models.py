from datetime import UTC, datetime

import shortuuid
import sqlalchemy as sa
from sqlalchemy import DateTime, MetaData, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID

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


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=db_naming_convention)


class BaseSQLModel(Base):
    __abstract__ = True

    # ! if uid and id are computed at SQL level, we should add `| None` on the typing,
    # and add `default=None` in mapped_column.
    # Here both of uid and id columns are computed at python level, so no need to add `| None`
    uid: Mapped[str] = mapped_column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
    id: Mapped[str] = mapped_column(
        String(22),
        index=True,
        nullable=False,
        unique=True,
        default=shortuuid.uuid,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        # if relationship changes, for e.g. set one more user in a team
        # the updated_at won't be updated automatically
        onupdate=sa.func.now(),
    )
