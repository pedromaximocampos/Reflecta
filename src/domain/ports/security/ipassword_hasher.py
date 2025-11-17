from abc import ABC, abstractmethod
from src.domain.value_objects.password_hash import PasswordHash

class IPasswordHasher(ABC):

    @abstractmethod
    def hash(self, raw_password: str) -> PasswordHash:
        """Gera um hash seguro para a senha fornecida."""
        pass

    @abstractmethod
    def verify(self, raw_password: str, hashed_password: PasswordHash) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        pass

    @abstractmethod
    def needs_rehash(self, hashed_password: PasswordHash) -> bool:
        """Verifica se o hash da senha precisa ser atualizado para um padrão mais seguro."""
        pass