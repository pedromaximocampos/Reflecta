from abc import ABC, abstractmethod
from src.domain.entities.user import User
from typing import Optional

class IUserRepository(ABC):
    """Contrato do repositório de User (domínio não conhece Mongo/Flask)."""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Retorna usuário por id ou None."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Retorna usuário ativo por email ou None."""
        raise NotImplementedError


    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def update(self, user: User) -> None: ...


    @abstractmethod
    async def update_login(self, user: User) -> None: ...