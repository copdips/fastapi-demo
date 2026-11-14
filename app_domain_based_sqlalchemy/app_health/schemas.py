from typing import Any

from app_domain_based_sqlalchemy.app_common.schemas import BaseModel


class HealthRead(BaseModel):
    status: str
    message: str
    meta: dict[str, Any]
