from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel

from app.db.models.base_models import UserBase


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]


class UserRead(UserBase):
    # diff between UserRead and User is that User has team as Relationship
    # But db.models.user_composite_models.UserReadWithTeam(UserRead) has team as TeamRead
    # team in User is a relationship which is discarded in Pydantic model,
    # if we set endpoint response type to User, there won't be team field in the response
    # thus, we must use UserReadWithTeam as response type.
    id: str
    team_id: str | None
    created_at: datetime
    updated_at: datetime | None


class UserUpdate(SQLModel):
    # class without param (table=True) will be a simple Pydantic BaseModel
    """
    create UserUpdate in addition to User model to avoid updating id,
    and also need to set all the update fields optional for the UPDATE endpoint, not PUT
    ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/#heroupdate-model
    """

    model_config = ConfigDict(extra="forbid")  # type: ignore[assignment]

    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    team_id: str | None = None
