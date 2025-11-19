from typing import Optional
from dataclasses import dataclass

@dataclass(slots=True)
class LoginInput:
    email: str
    password: str

@dataclass(slots=True)
class LoginOutput:
    user_id: str
    username: str
    name: str
    surname: str
    email: str
    access_token: str
    refresh_token: str
    avatar_url: Optional[str] = None