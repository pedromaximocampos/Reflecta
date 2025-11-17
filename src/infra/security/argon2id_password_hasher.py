from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from argon2 import PasswordHasher
from src.domain.value_objects.password_hash import PasswordHash
from src.infra.security.configs.argon2.config import Argon2Config
from src.infra.security.configs.argon2.versions import  get_argon2_v1_config
from src.domain.exceptions.api_types import AuthError


CURRENT_ARGON2_VERSION = get_argon2_v1_config()

class Argon2IdPasswordHasher(IPasswordHasher):

    def __init__(self, config: Argon2Config = CURRENT_ARGON2_VERSION) -> None:
        self._config = config
        self._argon2 = PasswordHasher(
            time_cost=self._config.time_cost,
            memory_cost=self._config.memory_cost,
            parallelism=self._config.parallelism,
            hash_len=self._config.hash_len,
            salt_len=self._config.salt_len,
        )


    def hash(self, raw_password: str) -> PasswordHash:
        hashed_password = self._argon2.hash(raw_password)
        return PasswordHash(hash=hashed_password, version=self._config.version, algorithm=self._config.algorithm)

    def verify(self, raw_password: str, hashed_password: PasswordHash) -> bool:
        try:
            self._argon2.verify(hashed_password.hash, raw_password)
            return True
        except Exception as e:
            return False

    def needs_rehash(self, hashed_password: PasswordHash) -> bool:
        if hashed_password.version != self._config.version:
            return True

        return self._argon2.check_needs_rehash(hashed_password.hash)