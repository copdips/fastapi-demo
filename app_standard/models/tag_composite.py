from app_standard.models.tag import TagRead
from app_standard.models.team import TeamRead


class TagReadComposite(TagRead):
    teams: list[TeamRead] = []  # noqa: RUF012
