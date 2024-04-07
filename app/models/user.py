from email_validator import validate_email
from pydantic import EmailStr, field_validator
from sqlmodel import AutoString, Field

from app.models.base import BaseModel, BaseReadModel, ForbidExtraMixin


class UserBase(BaseModel):
    name: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    # EmailStr with sa_type=AutoString: https://github.com/tiangolo/sqlmodel/discussions/730#discussioncomment-7952622
    # or use: email: EmailStr = Field(sa_column=Column(String, index=True, unique=True))
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)

    @field_validator("email")
    @classmethod
    def verify_email(cls, v: str) -> EmailStr:
        _ = validate_email(v, check_deliverability=False)
        return v.lower()


class UserCreate(UserBase, ForbidExtraMixin): ...


class UserRead(UserBase, BaseReadModel):
    # diff between UserRead and User is that User has team as Relationship
    # But db.models.user_composite_models.UserReadWithTeam(UserRead) has team as TeamRead
    # team in User is a relationship which is discarded in Pydantic model,
    # if we set endpoint response type to User, there won't be team field in the response
    # thus, we must use UserReadWithTeam as response type.
    id: str
    # team_id: str | None
    # created_at: datetime
    # updated_at: datetime | None


class UserUpdate(BaseModel, ForbidExtraMixin):
    # class without param (table=True) will be a simple Pydantic BaseModel
    """
    create UserUpdate in addition to User model to avoid updating id,
    and also need to set all the update fields optional for the UPDATE endpoint, not PUT
    ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/#heroupdate-model
    """

    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    team_name: str | None = None
