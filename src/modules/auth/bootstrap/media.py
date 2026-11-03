from src.modules.auth.application.ports.media import IUserAvatarProcessor
from src.modules.auth.infrastructure.media import PillowUserAvatarProcessor


def get_user_avatar_processor() -> IUserAvatarProcessor:
    return PillowUserAvatarProcessor()
