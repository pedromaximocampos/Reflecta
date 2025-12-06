# tests/support/doubles/user_repository_fake.py
from typing import Iterable, Optional, Dict

from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.user_id import UserId


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
        self.calls_update_auth_credentials = 0
        self.calls_update_last_login_at = 0
        self.calls_create = 0
        self.calls_verify_email = 0

        # últimos argumentos / usuários manipulados
        self.last_find_by_id_arg: Optional[UserId] = None
        self.last_find_by_email_arg: Optional[Email] = None
        self.last_updated_user: Optional[User] = None
        self.last_created_user: Optional[User] = None

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        self.calls_find_by_id += 1
        self.last_find_by_id_arg = user_id
        return self._users_by_id.get(user_id)

    async def find_by_email(self, email: Email) -> Optional[User]:
        self.calls_find_by_email += 1
        self.last_find_by_email_arg = email
        for user in self._users_by_id.values():
            if user.email == email:
                return user
        return None

    async def update(self, user: User) -> None:
        self.calls_update += 1
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
