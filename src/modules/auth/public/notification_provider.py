from functools import lru_cache

from src.modules.auth.infrastructure.persistence.postgresql.user_notification_recipient_provider import (
    PostgresUserNotificationRecipientProvider,
)
from src.modules.auth.public.notification_recipient import (
    IUserNotificationRecipientProvider,
)
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)


@lru_cache
def get_user_notification_recipient_provider() -> IUserNotificationRecipientProvider:
    return PostgresUserNotificationRecipientProvider(individuum_mvp_provider)

