from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_domain_based_sqlalchemy.app_common.models import BaseSQLModel
from app_domain_based_sqlalchemy.model_relationships.model_relationships import TagTeamLink

if TYPE_CHECKING:
    from app_domain_based_sqlalchemy.app_tag.models import Tag
    from app_domain_based_sqlalchemy.app_user.models import User


class Team(BaseSQLModel):
    __tablename__ = "team"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    headquarters: Mapped[str] = mapped_column(String(200))

    # one-to-many relationship [one side]
    # implicit IO is not allowed under asyncio: eager load with selectinload(Team.users)
    users: Mapped[list["User"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
    )
    # many-to-many relationship through the TagTeamLink table
    tags: Mapped[list["Tag"]] = relationship(
        secondary=TagTeamLink.__table__,
        back_populates="teams",
    )
