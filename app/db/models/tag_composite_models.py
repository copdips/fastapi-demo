from app.db.models.tag_models import TagRead
from app.db.models.team_models import TeamRead


class TagReadComposite(TagRead):
    teams: list[TeamRead] = []  # noqa: RUF012
