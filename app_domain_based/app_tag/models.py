from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlmodel import Relationship

from app_domain_based.app_common.models import BaseSQLModel
from app_domain_based.app_tag.schemas import TagBase
from app_domain_based.model_relationships.model_relationships import TagTeamLink

if TYPE_CHECKING:
    # https://sqlmodel.tiangolo.com/tutorial/code-structure/#import-only-while-editing-with-type_checking
    from app_domain_based.app_team.models import Team


class Tag(BaseSQLModel, TagBase, table=True):
    # one-to-many relationship [one side]: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/#add-teams-models
    # cannot use list[User] as by this point the Python interpreter doesn't know of any class User.
    # But the editor and other tools can see that the string is actually a type annotation inside,
    # and provide all the autocompletion, type checks, etc
    teams: Mapped[list["Team"]] = Relationship(
        back_populates="tags",
        link_model=TagTeamLink,
    )
