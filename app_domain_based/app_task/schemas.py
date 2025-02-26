from datetime import UTC, datetime
from typing import Any, Self

from pydantic import computed_field, model_validator
from sqlmodel import JSON, Column, Field, SQLModel

from app_domain_based.app_common.schemas import (
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
    def format_emails(self) -> Self:
        def _format_emails(v) -> list[str]:
            return list({email.lower() for email in v})

        self["on_done"] = _format_emails(self.get("on_done") or [])
        self["on_failed"] = _format_emails(self.get("on_failed") or [])
        self["on_all"] = _format_emails(self.get("on_all") or [])
        return self


class TaskBase(BaseModel):
    name: str
    type: str
    status: TaskStatus = Field(default=TaskStatus.in_progress)
    description: str | None = None
    created_by: str | None = None
    message: str | None = None
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
