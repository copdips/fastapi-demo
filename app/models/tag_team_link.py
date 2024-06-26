from app.models.base import BaseModel


class TagTeamLinkUpdate(BaseModel):
    tag_id: str
    team_id: str


class TagTeamLinkDelete(BaseModel):
    tag_id: str
    team_id: str
