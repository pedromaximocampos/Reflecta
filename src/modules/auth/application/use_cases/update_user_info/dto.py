from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.modules.auth.public.user_id import UserId


@dataclass(frozen=True, slots=True)
class UpdateUserInfoInput:
    user_id: UserId
    name: Optional[str] = None
    surname: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None


@dataclass(frozen=True, slots=True)
class UpdateUserInfoOutput:
    user_id: UserId
    name: str
    surname: str
    date_of_birth: date
    avatar_url: Optional[str]
