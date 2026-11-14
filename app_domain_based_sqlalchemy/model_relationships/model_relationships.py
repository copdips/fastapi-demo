from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app_domain_based_sqlalchemy.app_common.models import Base


class TagTeamLink(Base):
    """Association table between Tag and Team.

    ! if extra fields are needed (name, description, ...), add them here and
    declare the relationship with an association object instead of `secondary`.
    """

    __tablename__ = "tag_team_link"

    tag_id: Mapped[str] = mapped_column(
        String(22),
        ForeignKey("tag.id"),
        primary_key=True,
    )
    team_id: Mapped[str] = mapped_column(
        String(22),
        ForeignKey("team.id"),
        primary_key=True,
    )
