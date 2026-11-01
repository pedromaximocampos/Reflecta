import logging

from src.modules.auth.application.ports.storage import IUserAvatarStorage
from src.modules.auth.domain.entities.user import User


_LOGGER = logging.getLogger(__name__)


async def resolve_user_avatar_url(
    user: User,
    storage: IUserAvatarStorage,
) -> str | None:
    if not user.avatar_object_key:
        return user.avatar_url
    try:
        return await storage.create_read_url(object_key=user.avatar_object_key)
    except Exception:
        _LOGGER.exception(
            "Failed to resolve user avatar URL: user_id=%s",
            user.id.value,
        )
        return user.avatar_url
