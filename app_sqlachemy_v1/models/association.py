from sqlalchemy.sql.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import Integer

from app_sqlachemy_v1.models.base import Base

user_tag_association = Table(
    "user_tag_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)
