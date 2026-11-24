from sqlalchemy import select

from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import (
    UserModel,
)
from src.modules.auth.public.notification_recipient import (
    IUserNotificationRecipientProvider,
    UserNotificationRecipient,
    UserNotificationRecipientUnavailable,
)


class PostgresUserNotificationRecipientProvider(IUserNotificationRecipientProvider):
    def __init__(self, db) -> None:
        self._db = db

    async def get_active_recipient(self, user_id: str) -> UserNotificationRecipient:
        async with self._db.session() as session:
            user = await session.scalar(
                select(UserModel).where(
                    UserModel.id == user_id,
                    UserModel.deleted_at.is_(None),
                )
            )
        if user is None:
            raise UserNotificationRecipientUnavailable()
        return UserNotificationRecipient(
            user_id=user.id,
            username=user.username,
            email=user.email,
        )

