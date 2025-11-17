from dataclasses import dataclass
from src.domain.value_objects.password_algorithm import PasswordAlgorithm


@dataclass(frozen=True, slots=True)
class Argon2Config:
    time_cost: int
    memory_cost: int
    parallelism: int
    version: int
    hash_len: int = 32
    salt_len: int = 16
    algorithm: PasswordAlgorithm = PasswordAlgorithm.ARGON2ID
