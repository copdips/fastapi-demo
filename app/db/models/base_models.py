from datetime import UTC, datetime

import sqlalchemy as sa
from sqlmodel import Field, SQLModel
from ulid import ULID


class BaseSQLModel(SQLModel):
    id: str | None = Field(default_factory=lambda: str(ULID()), primary_key=True)
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


class UserBase(SQLModel):
    name: str = Field(unique=True, index=True)
    first_name: str
    last_name: str


class TeamBase(SQLModel):
    name: str = Field(unique=True, index=True)
    headquarters: str


class TagBase(SQLModel):
    name: str = Field(unique=True, index=True)