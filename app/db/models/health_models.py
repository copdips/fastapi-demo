from sqlmodel import SQLModel


class HealthRead(SQLModel):
    status: str
    message: str
    meta: dict
