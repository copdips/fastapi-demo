from sqlalchemy.orm import relationship

from app_sqlalchemy_v1.models.base import Base, BaseMixin


class Team(BaseMixin, Base):
    users = relationship("User", back_populates="team")
