from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app_sqlachemy_v1.models.base import Base
from app_sqlachemy_v1.models.association import user_tag_association

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("User", secondary=user_tag_association, back_populates="tags")
