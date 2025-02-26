from datetime import datetime, timedelta

import sqlalchemy as sa
from pydantic import field_validator
from sqlmodel import Field

from app_domain_based.app_common.models import BaseSQLModel
from app_domain_based.app_task.schemas import EmailNotification, TaskBase


class Task(BaseSQLModel, TaskBase, table=True):
    ended_at: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))
    task_duration: timedelta | None = None

    @field_validator("email_notification")
    @classmethod
    def email_notification_to_dict(cls, v: EmailNotification):
        # ! without this dump, nested model like email_notification cannot be save into DB by sqlalchemey
        # ref: https://github.com/tiangolo/sqlmodel/issues/63#issuecomment-1008320560
        # ref: https://github.com/sqlalchemy/sqlalchemy/blob/a124a593c86325389a92903d2b61f40c34f6d6e2/lib/sqlalchemy/sql/sqltypes.py#L2680
        return v.model_dump()
