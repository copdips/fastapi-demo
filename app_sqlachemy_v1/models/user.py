from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app_sqlachemy_v1.models.base import Base

from app_sqlachemy_v1.models.association import user_tag_association

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))

    team = relationship("Team", back_populates="users")
    tags = relationship("Tag", secondary=user_tag_association, back_populates="users")
