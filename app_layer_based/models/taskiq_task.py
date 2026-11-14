from app_layer_based.models.base import BaseModel


class TaskiqTaskBase(BaseModel):
    task_id: str


class TaskiqTaskCreate(TaskiqTaskBase): ...
