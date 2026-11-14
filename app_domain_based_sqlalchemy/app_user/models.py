from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_domain_based_sqlalchemy.app_common.models import BaseSQLModel

if TYPE_CHECKING:
    # only for type checking: the mapper resolves the string name at runtime.
    from app_domain_based_sqlalchemy.app_team.models import Team


class User(BaseSQLModel):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)

    # one-to-many relationship [many side]
    team_id: Mapped[str | None] = mapped_column(ForeignKey("team.id"), default=None)
    team: Mapped["Team | None"] = relationship(back_populates="users")
