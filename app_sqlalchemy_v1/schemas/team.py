
from pydantic import BaseModel


class TeamCreate(BaseModel): ...


class TeamRead(BaseModel):
    id: str
    name: str
