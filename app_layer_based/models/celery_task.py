from app_layer_based.models.base import BaseModel


class CeleryTaskBase(BaseModel):
    task_id: str


class CeleryTaskCreate(CeleryTaskBase): ...
