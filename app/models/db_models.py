from uuid import UUID

from sqlmodel import Field, MetaData, Relationship, SQLModel

from app.models.base_models import BaseModel, BaseSQLModel, TagBase, TeamBase, UserBase

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


class TagTeamLink(BaseModel, table=True):
    # ! if need extra fields, for example, name, description, etc, add them here,
    # need to add Relationship:
    # https://sqlmodel.tiangolo.com/tutorial/many-to-many/link-with-extra-fields/
    tag_id: UUID | None = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
    )
    team_id: UUID | None = Field(
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
    users: list["User"] = Relationship(
        back_populates="team",
        # ! if need cascade delete at ORM level, need to declare it at FK level from one-to-many, one side.
        # ! for sql raw level cascade delete, need to declare it at FK level from one-to-many, many side.
        sa_relationship_kwargs={
            "cascade": "all,delete,delete-orphan",
        },
    )
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
    tags: list["Tag"] = Relationship(
        back_populates="teams",
        link_model=TagTeamLink,
    )


class User(BaseSQLModel, UserBase, table=True):
    # __tablename__ = "user"  # Optional, default to snake case of class name
    # one-to-many relationship [many side]: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/#update-hero-models
    # declare team because in Team model, team defined as back_populates for users
    team_id: UUID | None = Field(
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
    team: Team | None = Relationship(back_populates="users")
    # ! team can be declared with Optional["Team"] to avoid circular import
    # ref: https://sqlmodel.tiangolo.com/tutorial/code-structure/#hero-model-file
    # from typing import Optional
    # team: Optional["Team"] | None = Relationship(back_populates="users")


class Tag(BaseSQLModel, TagBase, table=True):
    # one-to-many relationship [one side]: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/#add-teams-models
    # cannot use list[User] as by this point the Python interpreter doesn't know of any class User.
    # But the editor and other tools can see that the string is actually a type annotation inside,
    # and provide all the autocompletion, type checks, etc
    teams: list["Team"] = Relationship(back_populates="tags", link_model=TagTeamLink)
