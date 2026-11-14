from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_domain_based_sqlalchemy.app_common.models import BaseSQLModel
from app_domain_based_sqlalchemy.model_relationships.model_relationships import TagTeamLink

if TYPE_CHECKING:
    from app_domain_based_sqlalchemy.app_team.models import Team


class Tag(BaseSQLModel):
    __tablename__ = "tag"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # many-to-many relationship through the TagTeamLink table
    teams: Mapped[list["Team"]] = relationship(
        secondary=TagTeamLink.__table__,
        back_populates="tags",
    )
