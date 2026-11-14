from app_layer_based_sqlmodel.models.tag import TagRead
from app_layer_based_sqlmodel.models.team import TeamRead
from app_layer_based_sqlmodel.models.user import UserRead


class TeamReadComposite(TeamRead):
    tags: list[TagRead] = []  # noqa: RUF012
    users: list[UserRead] = []  # noqa: RUF012
