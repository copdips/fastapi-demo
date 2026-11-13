from app_standard.models.base import BaseModel


class TaskiqTaskBase(BaseModel):
    task_id: str


class TaskiqTaskCreate(TaskiqTaskBase): ...
