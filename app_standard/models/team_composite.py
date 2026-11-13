from app_standard.models.tag import TagRead
from app_standard.models.team import TeamRead
from app_standard.models.user import UserRead


class TeamReadComposite(TeamRead):
    tags: list[TagRead] = []  # noqa: RUF012
    users: list[UserRead] = []  # noqa: RUF012
