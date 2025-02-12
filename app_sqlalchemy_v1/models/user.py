from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app_sqlalchemy_v1.models.base import Base, BaseMixin


class User(BaseMixin, Base):
    team_id = Column(String, ForeignKey("team.id"))
    # ! if miss typing team_id to Integer, SQLITE won't raise any error, but PostgreSQL does
    # team_id = Column(Integer, ForeignKey("team.id"))

    team = relationship("Team", back_populates="users")
    # tags = relationship("Tag", secondary=user_tag_association, back_populates="users")

    # e.g. from: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object
    tags = relationship("UserTagAssociation", back_populates="user")
