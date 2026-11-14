from app_layer_based_sqlmodel.models.tag import TagRead
from app_layer_based_sqlmodel.models.team import TeamRead


class TagReadComposite(TagRead):
    teams: list[TeamRead] = []  # noqa: RUF012
