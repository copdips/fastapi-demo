from sqlmodel import SQLModel


class TagTeamLinkUpdate(SQLModel):
    tag_id: str
    team_id: str


class TagTeamLinkDelete(SQLModel):
    tag_id: str
    team_id: str
