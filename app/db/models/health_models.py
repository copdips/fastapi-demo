from typing import Any

from app.db.models.base_models import BaseModel


class HealthRead(BaseModel):
    status: str
    message: str
    meta: dict[str, Any]
