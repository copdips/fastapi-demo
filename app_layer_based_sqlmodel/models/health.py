from typing import Any

from app_layer_based_sqlmodel.models.base import BaseModel


class HealthRead(BaseModel):
    status: str
    message: str
    meta: dict[str, Any]
