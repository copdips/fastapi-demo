import logging
from collections.abc import Sequence

from fastapi import Query
from sqlalchemy.orm import selectinload
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.db import Tag, Team, User
from app.models.team import TeamCreate, TeamUpdate
from app.services.base import BaseService


class TeamService(BaseService[Team]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, Team, logger)

    async def create(self, team: TeamCreate) -> Team:
        db_team = Team.model_validate(team)
        self.session.add(db_team)
        await self.session.commit()
        return db_team

    async def get(self, team_id: str) -> Team:
        # selectinload(Team.users) for eager loading
        # team = await self.session.get(Team, team_id, options=[selectinload(Team.users)])
        """
        with selectinload:
        ! team = await self.session.get(Team, team_id, options=[selectinload(Team.users)])

        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        INFO sqlalchemy.engine.Engine
            SELECT team.name AS team_name, team.id AS team_id, team.created_at AS team_created_at, team.updated_at AS team_updated_at, team.headquarters AS team_headquarters
            FROM team
            WHERE team.id = $1::VARCHAR
        INFO sqlalchemy.engine.Engine [generated in 0.00080s] ('01HSGMMWS7PPXF62NDG64NRZC2',)
        INFO sqlalchemy.engine.Engine
            SELECT "user".team_id AS user_team_id, "user".name AS user_name, "user".first_name AS user_first_name, "user".last_name AS user_last_name, "user".id AS user_id, "user".created_at AS user_created_at, "user".updated_at AS user_updated_at
            FROM "user"
            WHERE "user".team_id IN ($1::VARCHAR)
        INFO sqlalchemy.engine.Engine [cached since 10.13s ago] ('01HSGMMWS7PPXF62NDG64NRZC2',)
        """

        """
        with subqueryload:
        ! team = await self.session.get(Team, team_id, options=[subqueryload(Team.users)])

        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        INFO sqlalchemy.engine.Engine
            SELECT team.name AS team_name, team.id AS team_id, team.created_at AS team_created_at, team.updated_at AS team_updated_at, team.headquarters AS team_headquarters
            FROM team
            WHERE team.id = $1::VARCHAR
        INFO sqlalchemy.engine.Engine [generated in 0.00037s] ('01HSGM4SR892PFPHEDJRNPYVCH',)
        INFO sqlalchemy.engine.Engine
            SELECT "user".name AS user_name, "user".first_name AS user_first_name, "user".last_name AS user_last_name, "user".id AS user_id, "user".created_at AS user_created_at, "user".updated_at AS user_updated_at, "user".team_id AS user_team_id, anon_1.team_id AS anon_1_team_id
            FROM (SELECT team.id AS team_id
            FROM team
            WHERE team.id = $1::VARCHAR) AS anon_1 JOIN "user" ON anon_1.team_id = "user".team_id
        INFO sqlalchemy.engine.Engine [generated in 0.00071s] ('01HSGM4SR892PFPHEDJRNPYVCH',)
        """

        """
        with joinedload:  (this one has less sql queries than the other two methods)
        ! team = await self.session.get(Team, team_id, options=[joinedload(Team.users)])

        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        INFO sqlalchemy.engine.Engine
            SELECT team.name AS team_name, team.id AS team_id, team.created_at AS team_created_at, team.updated_at AS team_updated_at, team.headquarters AS team_headquarters, user_1.name AS user_1_name, user_1.first_name AS user_1_first_name, user_1.last_name AS user_1_last_name, user_1.id AS user_1_id, user_1.created_at AS user_1_created_at, user_1.updated_at AS user_1_updated_at, user_1.team_id AS user_1_team_id
            FROM team LEFT OUTER JOIN "user" AS user_1 ON team.id = user_1.team_id
            WHERE team.id = $1::VARCHAR
        INFO sqlalchemy.engine.Engine [generated in 0.00066s] ('01HSGMF5S7ZG0QGTH49XNYBY1F',)
        """
        return await self.get_by_id(
            team_id,
            [Team.tags, Team.users],
        )

    async def get_many(
        self,
        offset: int = 0,
        limit: int = Query(default=100, le=100),
    ) -> Sequence[Team]:
        # selectinload(Team.users) for eager loading
        """
        with selectinload to load many teams with users:
        ! (await self.session.exec(select(Team).options(selectinload(Team.users)).offset(offset).limit(limit))).all()
        ! ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#select-in-loading
        ! In most cases, selectin loading is the most simple and efficient way to eagerly load collections of objects.
        ! user selectinload() to load one-to-many or many-to-many relationship
        ! The only scenario in which selectin eager loading is not feasible is when the model is using composite primary keys,
        ! and the backend database does not support tuples with IN (for e.g.  Microsoft SQL Server, after check, it should support now), which currently includes SQL Server.

        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        INFO sqlalchemy.engine.Engine
            SELECT team.name, team.id, team.created_at, team.updated_at, team.headquarters
            FROM team
            LIMIT $1::INTEGER OFFSET $2::INTEGER
        INFO sqlalchemy.engine.Engine [generated in 0.00092s] (100, 0)
        INFO sqlalchemy.engine.Engine
            SELECT "user".team_id AS user_team_id, "user".name AS user_name, "user".first_name AS user_first_name, "user".last_name AS user_last_name, "user".id AS user_id, "user".created_at AS user_created_at, "user".updated_at AS user_updated_at
            FROM "user"
            WHERE "user".team_id IN ($1::VARCHAR, $2::VARCHAR, $3::VARCHAR)
        INFO sqlalchemy.engine.Engine [generated in 0.00083s] ('01HSGMBAAC9FM44CE2AP12JR4K', '01HSGMBAAD0Y1MAB34P1D915WW', '01HSGMBAAD9QHFZ320S1JMD2BF')
        INFO sqlalchemy.engine.Engine ROLLBACK
        """

        """
        with subqueryload to load many teams with users:
        ! (await self.session.exec(select(Team).options(subqueryload(Team.users)).offset(offset).limit(limit))).all()
        ! ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#subquery-eager-loading
        ! The subqueryload() eager loader is mostly legacy at this point, superseded by the selectinload() strategy which is of much simpler design.
        ! subqueryload() may continue to be useful for the specific case of an eager loaded collection for objects that use composite primary keys, on the Microsoft SQL Server backend that continues to not have support for the “tuple IN” syntax.


        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        INFO sqlalchemy.engine.Engine
            SELECT team.name, team.id, team.created_at, team.updated_at, team.headquarters
            FROM team
            LIMIT $1::INTEGER OFFSET $2::INTEGER
        INFO sqlalchemy.engine.Engine [generated in 0.00024s] (100, 0)
        INFO sqlalchemy.engine.Engine
            SELECT "user".name AS user_name, "user".first_name AS user_first_name, "user".last_name AS user_last_name, "user".id AS user_id, "user".created_at AS user_created_at, "user".updated_at AS user_updated_at, "user".team_id AS user_team_id, anon_1.team_id AS anon_1_team_id
            FROM (SELECT team.id AS team_id
            FROM team
            LIMIT $1::INTEGER OFFSET $2::INTEGER) AS anon_1 JOIN "user" ON anon_1.team_id = "user".team_id
        INFO sqlalchemy.engine.Engine [generated in 0.00038s] (100, 0)
        INFO sqlalchemy.engine.Engine ROLLBACK
        """

        """
        with joinedload to load many teams with users:
        ! use joinedload() to load many-to-one relationship
        ! as best practice, joinedload() should be used with many-to-one, so not good to use team-to-users here.
        ! must add unique() for one-to-many or many-to-many relationship (in this case team-to-users),
        ! When including joinedload() in reference to a one-to-many or many-to-many collection, the Result.unique() method must be applied to the returned result,
        ! which will uniquify the incoming rows by primary key that otherwise are multiplied out by the join. The ORM will raise an error if this is not present.
        ! ref: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#joined-eager-loading
        ! (await self.session.exec(select(Team).options(subqueryload(Team.users)).offset(offset).limit(limit))).unique().all()

        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        INFO sqlalchemy.engine.Engine
            SELECT anon_1.name, anon_1.id, anon_1.created_at, anon_1.updated_at, anon_1.headquarters, user_1.name AS name_1, user_1.first_name, user_1.last_name, user_1.id AS id_1, user_1.created_at AS created_at_1, user_1.updated_at AS updated_at_1, user_1.team_id
            FROM (SELECT team.name AS name, team.id AS id, team.created_at AS created_at, team.updated_at AS updated_at, team.headquarters AS headquarters
            FROM team
            LIMIT $1::INTEGER OFFSET $2::INTEGER) AS anon_1 JOIN "user" AS user_1 ON anon_1.id = user_1.team_id
        INFO sqlalchemy.engine.Engine [generated in 0.00018s] (100, 0)
        INFO sqlalchemy.engine.Engine ROLLBACK
        """
        query = (
            select(Team)
            .options(selectinload(Team.tags))
            .options(selectinload(Team.users))
            .offset(offset)
            .limit(limit)
        )
        # using join query can also get User data, but the result is tuple where each element is a pair of (Team, User)
        # if a team has 3 users, the result will be 3 tuples of (Team, User), which is not convenient.
        # query = select(Team, User).join(User).offset(offset).limit(limit)
        # ref: https://github.com/tiangolo/sqlmodel/issues/643#issuecomment-2010763043
        return (await self.session.exec(query)).all()

    async def update(self, team_id: str, new_data: TeamUpdate) -> Team:
        team = await self.get_by_id(team_id, [Team.tags, Team.users])
        """
        instead of `get_by_id` with `selectin_attributes=[Team.tags, Team.users]`,
        we can also use below code to load related tags and users eagerly:

            team = await self.get_by_id(team_id)
            await team.awaitable_attrs.tags
            await team.awaitable_attrs.users

        It is not necessary to use `team.tags = await team.awaitable_attrs.tags`,
        as `await team.awaitable_attrs.tags` populates team.tags automatically.

        The outcome of this solution is that after: `await self.session.refresh(team)`,
        team.tags and team.users will be purged, and if the route response model
        requests tags and users fields, we will get Pydantic validation error.
        We must call `team.awaitable_attrs` again to fix the error.

        But if we use `team = await self.get_by_id(team_id, [Team.tags, Team.users])`,
        after: `await self.session.refresh(team)`, team.tags and team.users are still
        there, and also updated.
        """
        team_data_dump = new_data.model_dump(exclude_unset=True)
        if "users_names" in team_data_dump:
            team.users = []
            users: Sequence[User] = []
            if users_names := set(team_data_dump.pop("users_names")):
                users = (
                    await self.session.exec(
                        select(User).where(col(User.name).in_(users_names)),
                    )
                ).all()
                if len(users) != len(users_names):
                    msg = "Some users not found."
                    raise NotFoundError(msg)
            team.users.extend(users)
        if "tags_names" in team_data_dump:
            team.tags = []
            tags: Sequence[Tag] = []
            if tags_names := set(team_data_dump.pop("tags_names")):
                tags = (
                    await self.session.exec(
                        select(Tag).where(col(Tag.name).in_(tags_names)),
                    )
                ).all()
                if len(tags) != len(tags_names):
                    msg = "Some tags not found."
                    raise NotFoundError(msg)
            team.tags.extend(tags)
        team.sqlmodel_update(team_data_dump)
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        # to get updated related tags and user, we don't need below awt_tags, awt_users, as team has already the updated data, even session.refresh is not needed.
        # but if you need to display updated_at in the API result, then session.refresh() is needed.

        return team
