from app.models.base import BaseModel


class CeleryTaskBase(BaseModel):
    task_id: str


class CeleryTaskCreate(CeleryTaskBase): ...
