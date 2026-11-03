from dataclasses import dataclass
from typing import BinaryIO

from src.modules.auth.public.user_id import UserId


@dataclass(frozen=True, slots=True)
class ReplaceUserAvatarInputDTO:
    user_id: UserId
    content: BinaryIO
    content_type: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class RemoveUserAvatarInputDTO:
    user_id: UserId
