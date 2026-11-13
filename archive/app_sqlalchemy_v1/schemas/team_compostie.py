from app_sqlalchemy_v1.schemas.team import TeamRead
from app_sqlalchemy_v1.schemas.user import UserRead


class TeamReadComposite(TeamRead):
    users: list[UserRead] = []  # noqa: RUF012
