from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from app_domain_based.app_common.models import BaseSQLModel
from app_domain_based.app_user.schemas import UserBase


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
    team : "Team" = Relationship(back_populates="users")
    # ! team can be declared with Optional["Team"] to avoid circular import
    # ref: https://sqlmodel.tiangolo.com/tutorial/code-structure/#hero-model-file
    # from typing import Optional
    # team: Optional["Team"] | None = Relationship(back_populates="users")
