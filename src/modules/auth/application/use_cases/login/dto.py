from typing import Optional
from dataclasses import dataclass
from src.modules.auth.public.user_id import UserId
from src.modules.auth.public.email import Email

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