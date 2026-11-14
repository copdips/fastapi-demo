from app_layer_based.models.tag import TagRead
from app_layer_based.models.team import TeamRead


class TagReadComposite(TagRead):
    teams: list[TeamRead] = []  # noqa: RUF012
