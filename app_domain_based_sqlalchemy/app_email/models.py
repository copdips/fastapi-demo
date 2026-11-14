from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app_domain_based_sqlalchemy.app_common.models import BaseSQLModel


class Email(BaseSQLModel):
    __tablename__ = "email"

    type: Mapped[str] = mapped_column(String(50))
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str | None] = mapped_column(Text, default=None)
    sender: Mapped[str | None] = mapped_column(String(320), default=None)
    to: Mapped[str | None] = mapped_column(Text, default=None)
    cc: Mapped[str | None] = mapped_column(Text, default=None)
    bcc: Mapped[str | None] = mapped_column(Text, default=None)
    tracking_id: Mapped[str | None] = mapped_column(String(100), default=None)
    # ! sort_order keeps this column last, matching the layer-based model's
    # ! column order; both layouts must describe the same table.
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        sort_order=100,
    )
