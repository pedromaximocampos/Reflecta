from datetime import datetime

from src.modules.auth.domain.entities.user import User
from typing import FrozenSet, Optional, Protocol
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId


class IUserRepository(Protocol):
    """Contrato do repositório de User (domínio não conhece Mongo/Flask)."""

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Retorna usuário não excluído por id ou None."""
        raise NotImplementedError

    async def find_by_email(self, email: Email) -> Optional[User]:
        """Retorna usuário ativo por email ou None."""
        raise NotImplementedError

    async def find_deleted_by_email(self, email: Email) -> Optional[User]: ...

    async def find_deleted_by_id(self, user_id: UserId) -> Optional[User]: ...

    async def update(self, user: User) -> None: ...

    async def update_user_info(
        self,
        user: User,
        fields_to_update: FrozenSet[str],
    ) -> None: ...

    async def update_auth_credentials(self, user: User) -> None: ...

    async def update_last_login_at(self, user: User) -> None: ...

    async def create(self, user: User) -> User: ...

    async def verify_email(self, user) -> User: ...

    async def mark_as_deleted(self, user_id: UserId, deleted_at: datetime) -> None: ...

    async def mark_as_recovered(self, user_id: UserId) -> None: ...
