from dataclasses import dataclass
from typing import Protocol


class UserNotificationRecipientUnavailable(Exception):
    """The account cannot receive application notifications."""


@dataclass(frozen=True, slots=True)
class UserNotificationRecipient:
    user_id: str
    username: str
    email: str


class IUserNotificationRecipientProvider(Protocol):
    async def get_active_recipient(self, user_id: str) -> UserNotificationRecipient: ...

