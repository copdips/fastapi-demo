from app_sqlalchemy_v1.schemas.team import TeamRead
from app_sqlalchemy_v1.schemas.user import UserRead


class UserReadComposite(UserRead):
    # ! use TeamRead for team instead of TeamReadComposite to avoid circular reference.
    # When team is loaded, there's no users attribute in the team object. That's OK.
    # https://sqlmodel.tiangolo.com/tutorial/code-structure/?h=cir#circular-imports
    team: TeamRead | None = None
