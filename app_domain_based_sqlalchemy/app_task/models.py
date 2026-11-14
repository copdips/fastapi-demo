from datetime import datetime, timedelta

from sqlalchemy import JSON, DateTime, Enum, Interval, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app_domain_based_sqlalchemy.app_common.models import BaseSQLModel
from app_domain_based_sqlalchemy.app_common.schemas import TaskStatus


class Task(BaseSQLModel):
    __tablename__ = "task"

    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(50))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.in_progress,
    )
    description: Mapped[str | None] = mapped_column(Text, default=None)
    created_by: Mapped[str | None] = mapped_column(String(100), default=None)
    message: Mapped[str | None] = mapped_column(Text, default=None)
    # ! nested pydantic models are dumped to dict by the schema before reaching the column
    email_notification: Mapped[dict | None] = mapped_column(JSON, default=None)
    context: Mapped[dict | None] = mapped_column(JSON, default=None)
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
    )
    task_duration: Mapped[timedelta | None] = mapped_column(Interval, default=None)
