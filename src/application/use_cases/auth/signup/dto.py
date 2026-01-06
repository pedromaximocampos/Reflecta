from dataclasses import dataclass
from datetime import date

from src.domain.entities.user import User
from src.domain.value_objects.email import Email


@dataclass(slots=True)
class SignupInputDTO:
    email: str
    password: str
    username: str
    name: str
    surname: str
    date_of_birth: date


@dataclass(slots=True)
class SignupOutputDTO:
    user: User


