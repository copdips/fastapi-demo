# ! currently, can not put `table=True` in class `BaseSQLModel`, need to debug
from sqlmodel import Field

from app_domain_based.app_common.schemas import BaseModel


class TagTeamLink(BaseModel, table=True):
    # ! if need extra fields, for example, name, description, etc, add them here,
    # need to add Relationship:
    # https://sqlmodel.tiangolo.com/tutorial/many-to-many/link-with-extra-fields/
    tag_id: str | None = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
    )
    team_id: str | None = Field(
        default=None,
        foreign_key="team.id",
        primary_key=True,
    )
