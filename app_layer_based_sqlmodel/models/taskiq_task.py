from app_layer_based_sqlmodel.models.base import BaseModel


class TaskiqTaskBase(BaseModel):
    task_id: str


class TaskiqTaskCreate(TaskiqTaskBase): ...
