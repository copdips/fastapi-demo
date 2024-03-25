from app.models.tag_models import TagRead
from app.models.team_models import TeamRead


class TagReadComposite(TagRead):
    teams: list[TeamRead] = []  # noqa: RUF012
