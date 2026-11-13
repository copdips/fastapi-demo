from typing import Any

from app_standard.models.base import BaseModel


class HealthRead(BaseModel):
    status: str
    message: str
    meta: dict[str, Any]
