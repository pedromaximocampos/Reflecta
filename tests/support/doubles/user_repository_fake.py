# tests/support/doubles/user_repository_fake.py
from datetime import datetime
from typing import Iterable, Optional, Dict

from src.modules.auth.domain.ports.repositories.iuser_repository import IUserRepository
from src.modules.auth.domain.entities.user import User
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId


class UserRepositoryFake(IUserRepository):
    """
    Fake in-memory de IUserRepository para testes unitários.
    Armazena usuários em dicionário e registra chamadas para asserções.
    """

    def __init__(self, initial_users: Iterable[User] | None = None) -> None:
        self._users_by_id: Dict[UserId, User] = {}
        if initial_users:
            for user in initial_users:
                self._users_by_id[user.id] = user

        # contadores de chamadas
        self.calls_find_by_id = 0
        self.calls_find_by_email = 0
        self.calls_update = 0
        self.calls_update_user_info = 0
        self.calls_update_auth_credentials = 0
        self.calls_update_last_login_at = 0
        self.calls_create = 0
        self.calls_verify_email = 0
        self.calls_mark_as_deleted = 0
        self.calls_mark_as_recovered = 0

        # últimos argumentos / usuários manipulados
        self.last_find_by_id_arg: Optional[UserId] = None
        self.last_find_by_email_arg: Optional[Email] = None
        self.last_updated_user: Optional[User] = None
        self.last_created_user: Optional[User] = None

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        self.calls_find_by_id += 1
        self.last_find_by_id_arg = user_id
        user = self._users_by_id.get(user_id)
        if user is None or user.is_deleted:
            return None
        return user

    async def find_by_email(self, email: Email) -> Optional[User]:
        self.calls_find_by_email += 1
        self.last_find_by_email_arg = email
        for user in self._users_by_id.values():
            if user.email == email and not user.is_deleted:
                return user
        return None

    async def find_deleted_by_email(self, email: Email) -> Optional[User]:
        for user in self._users_by_id.values():
            if user.email == email and user.is_deleted:
                return user
        return None

    async def find_deleted_by_id(self, user_id: UserId) -> Optional[User]:
        user = self._users_by_id.get(user_id)
        if user is None or not user.is_deleted:
            return None
        return user

    async def update(self, user: User) -> None:
        self.calls_update += 1
        self._users_by_id[user.id] = user
        self.last_updated_user = user

    async def update_user_info(self, user: User, fields_to_update: frozenset[str]) -> None:
        self.calls_update_user_info += 1
        self._users_by_id[user.id] = user
        self.last_updated_user = user

    async def update_auth_credentials(self, user: User) -> None:
        self.calls_update_auth_credentials += 1
        self._users_by_id[user.id] = user
        self.last_updated_user = user

    async def update_last_login_at(self, user: User) -> None:
        self.calls_update_last_login_at += 1
        self._users_by_id[user.id] = user
        self.last_updated_user = user

    async def create(self, user: User) -> User:
        self.calls_create += 1
        self._users_by_id[user.id] = user
        self.last_created_user = user
        return user

    async def verify_email(self, user: User) -> None:
        self.calls_verify_email += 1
        # se sua entidade tiver lógica de verificação, você pode aplicar aqui
        self._users_by_id[user.id] = user

    async def mark_as_deleted(self, user_id: UserId, deleted_at: datetime) -> None:
        self.calls_mark_as_deleted += 1
        user = self._users_by_id[user_id]
        user.mark_as_deleted(deleted_at)

    async def mark_as_recovered(self, user_id: UserId) -> None:
        self.calls_mark_as_recovered += 1
        self._users_by_id[user_id].mark_as_recovered()
