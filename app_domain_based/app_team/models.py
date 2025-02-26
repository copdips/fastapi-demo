from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlmodel import Relationship

from app_domain_based.app_common.models import BaseSQLModel
from app_domain_based.app_team.schemas import TeamBase
from app_domain_based.model_relationships.model_relationships import TagTeamLink

if TYPE_CHECKING:
    # https://sqlmodel.tiangolo.com/tutorial/code-structure/#import-only-while-editing-with-type_checking
    from app_domain_based.app_tag.models import Tag
    from app_domain_based.app_user.models import User

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
