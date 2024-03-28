from datetime import UTC, datetime
from uuid import UUID

from pydantic import ConfigDict, computed_field
from sqlmodel import Field, SQLModel

from app.models.base_models import BaseModel, TaskStatus


class TaskBase(BaseModel):
    name: str
    status: TaskStatus = Field(default=TaskStatus.in_progress)
    description: str | None = None
    trigger: str | None = None
    error: str | None = None


class TaskRead(TaskBase):
    id: UUID
    created_at: datetime
    ended_at: datetime | None = None

    @computed_field
    @property
    def task_duration_seconds(self) -> int | None:
        if self.status in (TaskStatus.done, TaskStatus.failed) and self.ended_at:
            return (self.ended_at - self.created_at).seconds
        return None


class TaskUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]
    status: TaskStatus | None = None
    description: str | None = None
    error: str | None = None

    @computed_field
    @property
    def ended_at(self) -> datetime | None:
        if self.status in (TaskStatus.done, TaskStatus.failed):
            return datetime.now(UTC)
        return None
