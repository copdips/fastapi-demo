
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str

class UserRead(BaseModel):
    # diff between UserRead and User is that User has team as Relationship
    # But db.models.user_composite_models.UserReadWithTeam(UserRead) has team as TeamRead
    # team in User is a relationship which is discarded in Pydantic model,
    # if we set endpoint response type to User, there won't be team field in the response
    # thus, we must use UserReadWithTeam as response type.
    id: str
    name: str

class UserUpdate(BaseModel):
    # class without param (table=True) will be a simple Pydantic BaseModel
    """
    create UserUpdate in addition to User model to avoid updating id,
    and also need to set all the update fields optional for the UPDATE endpoint, not PUT
    ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/#heroupdate-model
    """

    name: str | None = None
    team_name: str | None = None
