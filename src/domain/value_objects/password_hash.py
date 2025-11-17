from dataclasses import dataclass

from src.domain.value_objects.password_algorithm import PasswordAlgorithm


@dataclass(frozen=True, slots=True)
class PasswordHash:
    hash: str
    algorithm: PasswordAlgorithm
    version: int