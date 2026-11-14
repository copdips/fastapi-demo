from datetime import UTC, datetime
from typing import Any

from pydantic import computed_field, model_validator

from app_domain_based_sqlalchemy.app_common.schemas import (
    BaseModel,
    BaseReadModel,
    ForbidExtraMixin,
)
from app_domain_based_sqlalchemy.app_task.models import TaskStatus


class EmailNotification(BaseModel):
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
    name: str
    type: str
    status: TaskStatus = TaskStatus.in_progress
    description: str | None = None
    created_by: str | None = None
    message: str | None = None
    email_notification: EmailNotification | None = None
    context: dict[str, Any] | None = None


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


class TaskUpdate(BaseModel, ForbidExtraMixin):
    status: TaskStatus | None = None
    description: str | None = None
    message: str | None = None

    @computed_field
    @property
    def ended_at(self) -> datetime | None:
        if self.status in (TaskStatus.done, TaskStatus.failed):
            return datetime.now(UTC)
        return None
