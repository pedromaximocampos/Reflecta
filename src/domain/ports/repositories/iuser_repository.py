from abc import ABC, abstractmethod
from src.domain.entities.user import User
from typing import Optional

from src.domain.value_objects.email import Email
from src.domain.value_objects.user_id import UserId


class IUserRepository(ABC):
    """Contrato do repositório de User (domínio não conhece Mongo/Flask)."""

    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Retorna usuário por id ou None."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Retorna usuário ativo por email ou None."""
        raise NotImplementedError


    @abstractmethod
    async def update(self, user: User) -> None: ...

    @abstractmethod
    async def update_auth_credentials(self, user: User) -> None: ...


    @abstractmethod
    async def update_last_login_at(self, user: User) -> None: ...


    @abstractmethod
    async def create(self, user: User) -> User: ...