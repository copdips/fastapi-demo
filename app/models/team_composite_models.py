from app.models.tag_models import TagRead
from app.models.team_models import TeamRead
from app.models.user_models import UserRead


class TeamReadComposite(TeamRead):
    tags: list[TagRead] = []  # noqa: RUF012
    users: list[UserRead] = []  # noqa: RUF012
