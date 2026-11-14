from datetime import datetime

import sqlalchemy as sa
from email_validator import validate_email
from pydantic import field_validator
from sqlmodel import Field

from app_layer_based_sqlmodel.models.base import (
    BaseModel,
    BaseReadModel,
    ForbidExtraMixin,
)


class EmailBase(BaseModel):
    # column types mirror app_domain_based_sqlalchemy.app_email.models: one DB, one schema.
    type: str = Field(sa_type=sa.String(50))
    subject: str = Field(sa_type=sa.String(200))
    body: str | None = Field(default=None, sa_type=sa.Text())
    sender: str | None = Field(default=None, sa_type=sa.String(320))
    to: str | None = Field(default=None, sa_type=sa.Text())
    cc: str | None = Field(default=None, sa_type=sa.Text())
    bcc: str | None = Field(default=None, sa_type=sa.Text())
    tracking_id: str | None = Field(default=None, sa_type=sa.String(100))


class EmailCreate(EmailBase, ForbidExtraMixin):
    @field_validator("sender")
    @classmethod
    def validate_sender(cls, v: str) -> str:
        email = v.replace(" ", "")
        validate_email(email, check_deliverability=False)
        return email.lower()

    @field_validator("to", "cc", "bcc")
    @classmethod
    def validate_destinations(cls, v: str) -> str:
        emails = v.replace(" ", "").replace(";", ",").split(",")
        [validate_email(email, check_deliverability=False) for email in emails]
        return ",".join(emails).lower()


class EmailRead(EmailBase, BaseReadModel):
    id: str
    sent_at: datetime | None


class EmailUpdate(BaseModel, ForbidExtraMixin):
    type: str | None = None
    subject: str | None = None
    body: str | None = None
    tracking_id: str | None = None
    sent_at: datetime | None = None
