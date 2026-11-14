from email_validator import validate_email
from pydantic import EmailStr, field_validator

from app_domain_based_sqlalchemy.app_common.schemas import (
    BaseModel,
    BaseReadModel,
    ForbidExtraMixin,
)


class UserBase(BaseModel):
    name: str
    first_name: str
    last_name: str
    email: EmailStr

    @field_validator("email")
    @classmethod
    def verify_email(cls, v: str) -> EmailStr:
        _ = validate_email(v, check_deliverability=False)
        return v.lower()


class UserCreate(UserBase, ForbidExtraMixin): ...


class UserRead(UserBase, BaseReadModel):
    # the ORM User has `team` as a relationship, which is not part of this schema.
    # Use UserReadComposite when the response needs the team.
    id: str


class UserUpdate(BaseModel, ForbidExtraMixin):
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
