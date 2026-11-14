from datetime import UTC, datetime
from typing import Any

import sqlalchemy as sa
from pydantic import computed_field, model_validator
from sqlmodel import JSON, Column, Field, SQLModel

from app_layer_based_sqlmodel.models.base import (
    BaseModel,
    BaseReadModel,
    ForbidExtraMixin,
    TaskStatus,
)


class EmailNotification(SQLModel):
    on_done: list[str]
    on_failed: list[str]
    on_all: list[str]

    @model_validator(mode="before")
    @classmethod
    def format_emails(cls, data: Any) -> Any:
        def _format_emails(v) -> list[str]:
            return list({email.lower() for email in v})

        data["on_done"] = _format_emails(data.get("on_done") or [])
        data["on_failed"] = _format_emails(data.get("on_failed") or [])
        data["on_all"] = _format_emails(data.get("on_all") or [])
        return data


class TaskBase(BaseModel):
    # column types mirror app_domain_based_sqlalchemy.app_task.models: one DB, one schema.
    name: str = Field(sa_type=sa.String(200))
    type: str = Field(sa_type=sa.String(50))
    status: TaskStatus = Field(default=TaskStatus.in_progress)
    description: str | None = Field(default=None, sa_type=sa.Text())
    created_by: str | None = Field(default=None, sa_type=sa.String(100))
    message: str | None = Field(default=None, sa_type=sa.Text())
    email_notification: EmailNotification | None = Field(sa_column=Column(JSON))
    context: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))


class TaskRead(TaskBase, BaseReadModel):
    id: str
    created_at: datetime
    ended_at: datetime | None = None

    @computed_field
    @property
    def task_duration_seconds(self) -> int | None:
        if self.status in (TaskStatus.done, TaskStatus.failed) and self.ended_at:
            return (self.ended_at - self.created_at).seconds
        return None


class TaskUpdate(SQLModel, ForbidExtraMixin):
    status: TaskStatus | None = None
    description: str | None = None
    message: str | None = None

    @computed_field
    @property
    def ended_at(self) -> datetime | None:
        if self.status in (TaskStatus.done, TaskStatus.failed):
            return datetime.now(UTC)
        return None
