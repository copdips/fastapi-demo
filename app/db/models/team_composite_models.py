from app.db.models.tag_models import TagRead
from app.db.models.team_models import TeamRead
from app.db.models.user_models import UserRead


class TeamReadComposite(TeamRead):
    tags: list[TagRead] = []  # noqa: RUF012
    users: list[UserRead] = []  # noqa: RUF012
