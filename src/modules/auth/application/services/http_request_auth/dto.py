from dataclasses import dataclass
from typing import Optional
from src.modules.auth.public.user_id import UserId


@dataclass(frozen=True, slots=True)
class AuthenticatedUserDTO:
    user_id: UserId
    is_admin: bool = False
    roles: Optional[list[str]] = None