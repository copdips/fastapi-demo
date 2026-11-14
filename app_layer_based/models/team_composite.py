from app_layer_based.models.tag import TagRead
from app_layer_based.models.team import TeamRead
from app_layer_based.models.user import UserRead


class TeamReadComposite(TeamRead):
    tags: list[TagRead] = []  # noqa: RUF012
    users: list[UserRead] = []  # noqa: RUF012
