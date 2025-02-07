from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app_sqlachemy_v1.models.base import Base



class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("User", back_populates="team")
