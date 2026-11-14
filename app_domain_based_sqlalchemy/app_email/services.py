import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app_domain_based_sqlalchemy.app_common.repositories import BaseRepository
from app_domain_based_sqlalchemy.app_email.models import Email
from app_domain_based_sqlalchemy.app_email.schemas import EmailCreate, EmailUpdate
from app_domain_based_sqlalchemy.schema_composites.schema_composites import (
    UserReadCompositeOutOfAPI,
)

if TYPE_CHECKING:
    import logging

    from sqlalchemy.ext.asyncio import AsyncSession

    from app_domain_based_sqlalchemy.app_user.models import User
    from app_domain_based_sqlalchemy.app_user.schemas import UserUpdate


class EmailService(BaseRepository[Email]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, Email, logger)

    async def create(self, email: EmailCreate) -> Email:
        db_email = Email(**email.model_dump())
        self.session.add(db_email)
        await self.session.commit()
        return db_email

    async def update(self, email_id: str, new_data: EmailUpdate) -> Email:
        email = await self.get_by_id(email_id)
        email_data_dump = new_data.model_dump(exclude_unset=True)
        for key, value in email_data_dump.items():
            setattr(email, key, value)
        self.session.add(email)
        await self.session.commit()
        await self.session.refresh(email)
        return email

    async def send(self, email_id: str) -> Email:
        email: Email = await self.get_by_id(email_id)
        # ! send email logic here, asyncio.sleep to simulate sending email
        await asyncio.sleep(2)
        email_update = EmailUpdate(sent_at=datetime.now(UTC))
        email = await self.update(email_id, email_update)
        msg = f"Sent email: {email.id}"
        self.logger.info(msg)
        return email

    async def send_for_user_update(
        self,
        user: User,
        update_data: UserUpdate,
        user_before_update: User,
    ) -> Email:
        # ! cannot use UserReadCompositeOutOfAPI.model_validate(user_before_update.model_dump())
        # as relationship data (team here) will be discarded.
        # must use UserReadCompositeOutOfAPI.parse_obj(user_before_update)
        formatted_user_before_update = UserReadCompositeOutOfAPI.model_validate(
            user_before_update,
        )
        email = Email(
            type="notification",
            subject=f"User {user.name} properties change notification",
            body=(
                f"\nUser {user.name} got following properties changed:"
                f"\n    {update_data.model_dump(exclude_unset=True)}"
                f"\n\nBefore the change, it was:"
                f"\n    {formatted_user_before_update.model_dump()}"
            ),
            to=user.email,
        )
        self.session.add(email)
        await self.session.commit()
        return await self.send(email.id)
