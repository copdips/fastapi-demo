from datetime import UTC, datetime

from pydantic.alias_generators import to_snake
from sqlalchemy import Column, DateTime, MetaData, String
from sqlalchemy.orm import declarative_base, declarative_mixin, declared_attr
from ulid import ULID

Base = declarative_base()
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
Base.metadata = MetaData(naming_convention=db_naming_convention)


def get_ulid():
    return str(ULID())


@declarative_mixin
class BaseMixin:
    @declared_attr
    @classmethod
    def __tablename__(cls):
        return to_snake(cls.__name__)

    id = Column(String, default=lambda: str(ULID()), primary_key=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=UTC),
        onupdate=lambda: datetime.now(tz=UTC),
    )
