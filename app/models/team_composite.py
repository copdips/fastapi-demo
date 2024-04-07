from app.models.tag import TagRead
from app.models.team import TeamRead
from app.models.user import UserRead


class TeamReadComposite(TeamRead):
    tags: list[TagRead] = []  # noqa: RUF012
    users: list[UserRead] = []  # noqa: RUF012
