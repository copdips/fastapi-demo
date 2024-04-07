from app.models.team import TeamBase, TeamRead
from app.models.user import UserBase, UserRead

"""
Error when using lazy loading with [implicit IO](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession) in asyncio:
fastapi.exceptions.ResponseValidationError: 1 validation errors:
{'type': 'get_attribute_error', 'loc': ('response', 'team'), 'msg': "Error extracting attribute: MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)", 'input': User(last_name='Wilson', name='Deadpond', first_name='Dive', team_id='01HSETF21TN2CBJX692C6WJBGW', id='01HSETF21VS5NJA5VJHQN380HQ', created_at=datetime.datetime(2024, 3, 20, 20, 57, 24, 283187, tzinfo=datetime.timezone.utc), updated_at=None), 'ctx': {'error': "MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)"}, 'url': 'https://errors.pydantic.dev/2.6/v/get_attribute_error'}

Solution 1 - Use eager loading with selectinload(User.team) in query options:

    one user:
        user = await self.session.get(User, user_id, options=[selectinload(User.team)])

    many users:
        query = (
            select(User).options(selectinload(User.team)).offset(offset).limit(limit)
        )
        return (await self.session.exec(query)).all()
"""


class UserReadComposite(UserRead):
    # ! use TeamRead for team instead of TeamReadComposite to avoid circular reference.
    # When team is loaded, there's no users attribute in the team object. That's OK.
    # https://sqlmodel.tiangolo.com/tutorial/code-structure/?h=cir#circular-imports
    team: TeamRead | None = None


class UserReadCompositeOutOfAPI(UserBase):
    # model without BaseReadModel, so without HATEOAS links
    team: TeamBase | None = None
