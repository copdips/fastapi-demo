from sqlalchemy.orm import relationship

from app_sqlalchemy_v1.models.base import Base, BaseMixin


class Tag(BaseMixin, Base):
    # users = relationship("User", secondary=user_tag_association, back_populates="tags")

    # e.g. from: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object
    users = relationship("UserTagAssociation", back_populates="tag")
