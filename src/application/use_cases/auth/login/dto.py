from typing import Optional
from dataclasses import dataclass
from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.email import Email

@dataclass(slots=True)
class LoginInput:
    email: Email
    password: str

@dataclass(slots=True)
class LoginOutput:
    user_id: UserId
    username: str
    name: str
    surname: str
    email: Email
    access_token: str
    refresh_token: str
    avatar_url: Optional[str] = None