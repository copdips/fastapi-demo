from collections.abc import Awaitable
from datetime import UTC, datetime, timedelta

import shortuuid
import sqlalchemy as sa
from async_sqlmodel import AsyncSQLModel, AwaitableField
from pydantic import ConfigDict, field_validator
from sqlalchemy.orm import Mapped
from sqlmodel import Field, MetaData, Relationship, SQLModel
from ulid import ULID

from app.models.base import BaseModel
from app.models.email import EmailBase
from app.models.tag import TagBase
from app.models.task import EmailNotification, TaskBase
from app.models.team import TeamBase
from app.models.user import UserBase

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
    AsyncSQLModel,
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


class TagTeamLink(BaseModel, table=True):
    # ! if need extra fields, for example, name, description, etc, add them here,
    # need to add Relationship:
    # https://sqlmodel.tiangolo.com/tutorial/many-to-many/link-with-extra-fields/
    tag_id: str | None = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
    )
    team_id: str | None = Field(
        default=None,
        foreign_key="team.id",
        primary_key=True,
    )


class Team(BaseSQLModel, TeamBase, table=True):
    # one-to-many relationship [one side]: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/#add-teams-models
    # cannot use list[User] as by this point the Python interpreter doesn't know of any class User.
    # But the editor and other tools can see that the string is actually a type annotation inside,
    # and provide all the autocompletion, type checks, etc
    # TODO: try use selectinload: https://github.com/tiangolo/sqlmodel/discussions/613#discussioncomment-6410234
    users: Mapped[list["User"]] = Relationship(
        back_populates="team",
        # ! if need cascade delete at ORM level, need to declare it at FK level from one-to-many, one side.
        # ! for sql raw level cascade delete, need to declare it at FK level from one-to-many, many side.
        sa_relationship_kwargs={
            "cascade": "all,delete,delete-orphan",
        },
    )
    awt_users: Awaitable[list["User"]] = AwaitableField(field="users")
    """
    in sa_relationship_kwargs, we can specify also:
    sa_relationship_kwargs={
        "lazy": "selectin",
        "cascade": "all,delete,delete-orphan",
    },
    if we dont specify lazy, it will be lazy loading by default,
    which means that the related objects will be loaded from the database only when we access the relationship.
    and in asyncio, as implicit IO is not allowed, we need to specify the selectin
    or other eager loading strategy in the query explicitly, like below:
    ```python
    query = (
    select(Team)
    .options(selectinload(Team.tags))
    .options(selectinload(Team.users))
    .offset(offset)
    .limit(limit)
    )
    ```
    """
    tags: Mapped[list["Tag"]] = Relationship(
        back_populates="teams",
        link_model=TagTeamLink,
    )
    awt_tags: Awaitable[list["Tag"]] = AwaitableField(field="tags")


class User(BaseSQLModel, UserBase, table=True):
    # __tablename__ = "user"  # Optional, default to snake case of class name
    # one-to-many relationship [many side]: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/#update-hero-models
    # declare team because in Team model, team defined as back_populates for users
    team_id: str | None = Field(
        default=None,
        foreign_key="team.id",
        # sa_column_kwargs={
        #     "ondelete": "CASCADE",  # ! this syntax is not working, below is OK. ref: https://github.com/tiangolo/sqlmodel/discussions/863
        # },
    )

    # team_id: str | None = Field(
    #     sa_column=Column(
    #         String,
    #         # ! if need cascade delete at raw sql level from psql for e.g. out of ORM,
    #         # ! need to declare it at FK level from one-to-many, many side.
    #         ForeignKey("team.uid", ondelete="CASCADE"),
    #     )
    # )
    team: Mapped[Team | None] = Relationship(back_populates="users")
    # ! team can be declared with Optional["Team"] to avoid circular import
    # ref: https://sqlmodel.tiangolo.com/tutorial/code-structure/#hero-model-file
    # from typing import Optional
    # team: Optional["Team"] | None = Relationship(back_populates="users")
    awt_team: Awaitable[Team] = AwaitableField(field="team")


class Tag(BaseSQLModel, TagBase, table=True):
    # one-to-many relationship [one side]: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/#add-teams-models
    # cannot use list[User] as by this point the Python interpreter doesn't know of any class User.
    # But the editor and other tools can see that the string is actually a type annotation inside,
    # and provide all the autocompletion, type checks, etc
    teams: Mapped[list["Team"]] = Relationship(
        back_populates="tags",
        link_model=TagTeamLink,
    )
    awt_teams: Awaitable[list["Team"]] = AwaitableField(field="teams")


class Task(BaseSQLModel, TaskBase, table=True):
    ended_at: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))
    task_duration: timedelta | None = None

    @field_validator("email_notification")
    @classmethod
    def email_notification_to_dict(cls, v: EmailNotification):
        # ! without this dump, nested model like email_notification cannot be save into DB by sqlalchemey
        # ref: https://github.com/tiangolo/sqlmodel/issues/63#issuecomment-1008320560
        # ref: https://github.com/sqlalchemy/sqlalchemy/blob/a124a593c86325389a92903d2b61f40c34f6d6e2/lib/sqlalchemy/sql/sqltypes.py#L2680
        return v.model_dump()


class Email(BaseSQLModel, EmailBase, table=True): ...
