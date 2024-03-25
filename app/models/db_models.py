from sqlmodel import Field, Relationship, SQLModel

from app.models.base_models import BaseSQLModel, TagBase, TeamBase, UserBase


class TagTeamLink(SQLModel, table=True):
    __tablename__ = "tag_team_link"
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
    users: list["User"] = Relationship(back_populates="team")
    tags: list["Tag"] = Relationship(back_populates="teams", link_model=TagTeamLink)


class User(BaseSQLModel, UserBase, table=True):
    # __tablename__ = "user"  # Optional, default to snake case of class name
    # one-to-many relationship [many side]: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/#update-hero-models
    # declare team because in Team model, team defined as back_populates for users
    team_id: str | None = Field(default=None, foreign_key="team.id")
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
