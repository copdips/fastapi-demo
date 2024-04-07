from typing import Any

from app.models.base import BaseModel


class HealthRead(BaseModel):
    status: str
    message: str
    meta: dict[str, Any]
