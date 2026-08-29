from dataclasses import dataclass
from datetime import date

from src.modules.auth.domain.entities.user import User
from src.modules.auth.public.email import Email


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


