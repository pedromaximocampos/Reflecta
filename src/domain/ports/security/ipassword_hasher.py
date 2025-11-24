from typing import Protocol
from src.domain.value_objects.password_hash import PasswordHash

class IPasswordHasher(Protocol):


    def hash(self, raw_password: str) -> PasswordHash:
        """Gera um hash seguro para a senha fornecida."""
        pass


    def verify(self, raw_password: str, hashed_password: PasswordHash) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        pass


    def needs_rehash(self, hashed_password: PasswordHash) -> bool:
        """Verifica se o hash da senha precisa ser atualizado para um padrão mais seguro."""
        pass