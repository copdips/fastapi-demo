from datetime import datetime

from email_validator import validate_email
from pydantic import field_validator

from app.models.base_models import BaseModel, BaseReadModel, ForbidExtraMixin


class EmailBase(BaseModel):
    type: str
    subject: str
    body: str | None = None
    sender: str | None = None
    to: str | None = None
    cc: str | None = None
    bcc: str | None = None
    tracking_id: str | None = None


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
