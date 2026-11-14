from app_layer_based_sqlmodel.models.base import BaseModel


class CeleryTaskBase(BaseModel):
    task_id: str


class CeleryTaskCreate(CeleryTaskBase): ...
