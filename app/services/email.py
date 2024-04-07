import asyncio
import logging
from datetime import UTC, datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.db import Email, User
from app.models.email import EmailCreate, EmailUpdate
from app.models.user import UserUpdate
from app.models.user_composite import (
    UserReadCompositeOutOfAPI,
)
from app.services.base import BaseService


class EmailService(BaseService[Email]):
    def __init__(self, session: AsyncSession, logger: logging.Logger):
        super().__init__(session, Email, logger)

    async def create(self, email: EmailCreate) -> Email:
        db_email = Email.model_validate(email)
        self.session.add(email)
        await self.session.commit()
        return db_email

    async def update(self, email_id: str, new_data: EmailUpdate) -> Email:
        email = await self.get_by_id(email_id)
        email_data_dump = new_data.model_dump(exclude_unset=True)
        email.sqlmodel_update(email_data_dump)
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
        msg = f"Sent email: {email.model_dump()}"
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
        formatted_user_before_update = UserReadCompositeOutOfAPI.parse_obj(
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
