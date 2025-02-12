from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey, Table

from app_sqlalchemy_v1.models.base import Base

# user_tag_association = Table(
#     "user_tag_association",
#     Base.metadata,
#     Column("user_id", String, ForeignKey("user.id")),
#     Column("tag_id", String, ForeignKey("tag.id")),
# )


class UserTagAssociation(Base):
    # e.g. from: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object
    __tablename__ = "user_tag_association"
    user_id = Column(String, ForeignKey("user.id"), primary_key=True)
    tag_id = Column(String, ForeignKey("tag.id"), primary_key=True)
    extra_data = Column(String)
    user = relationship("User", back_populates="tags")
    tag = relationship("Tag", back_populates="users")
