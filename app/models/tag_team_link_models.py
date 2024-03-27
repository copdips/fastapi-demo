from uuid import UUID

from app.models.base_models import BaseModel


class TagTeamLinkUpdate(BaseModel):
    tag_id: UUID
    team_id: UUID


class TagTeamLinkDelete(BaseModel):
    tag_id: UUID
    team_id: UUID
