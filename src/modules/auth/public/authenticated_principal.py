from dataclasses import dataclass

from src.modules.auth.public.user_id import UserId
from src.modules.auth.public.user_role import UserRole


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    user_id: UserId
    role: UserRole

    @property
    def is_admin(self) -> bool:
        return self.role is UserRole.ADMIN
