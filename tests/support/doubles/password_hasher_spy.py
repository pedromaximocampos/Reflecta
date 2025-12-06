# tests/support/doubles/password_hasher_spy.py
from typing import List, Tuple

from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.value_objects.password_algorithm import PasswordAlgorithm
from src.domain.value_objects.password_hash import PasswordHash


class PasswordHasherSpy(IPasswordHasher):
    """
    Spy de IPasswordHasher para testes de casos de uso.

    - Registra chamadas de hash/verify/needs_rehash
    - Permite configurar os retornos para cada método
    """

    def __init__(self) -> None:
        # registros de chamadas
        self.hash_calls: List[str] = []
        self.verify_calls: List[Tuple[str, PasswordHash]] = []
        self.needs_rehash_calls: List[PasswordHash] = []

        # valores padrão
        self._verify_return: bool = True
        self._needs_rehash_return: bool = False
        self._hash_return: PasswordHash = PasswordHash(
            algorithm=PasswordAlgorithm("argon2"),
            hash="hashed_password_default",
            version=1,
        )

    # helpers pra configurar comportamento nos testes

    def set_verify_result(self, value: bool) -> None:
        self._verify_return = value

    def set_needs_rehash_result(self, value: bool) -> None:
        self._needs_rehash_return = value

    def set_hash_return(self, password_hash: PasswordHash) -> None:
        self._hash_return = password_hash

    # implementação do contrato

    def hash(self, raw_password: str) -> PasswordHash:
        self.hash_calls.append(raw_password)
        return self._hash_return

    def verify(self, raw_password: str, hashed_password: PasswordHash) -> bool:
        self.verify_calls.append((raw_password, hashed_password))
        return self._verify_return

    def needs_rehash(self, hashed_password: PasswordHash) -> bool:
        self.needs_rehash_calls.append(hashed_password)
        return self._needs_rehash_return
