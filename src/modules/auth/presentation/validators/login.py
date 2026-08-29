from pydantic import BaseModel, EmailStr
from typing import Optional

class UserResponseValidator(BaseModel):
    email: EmailStr
    name: str
    surname: str
    username: str
    avatar_url: Optional[str] = None

class LoginRequestValidator(BaseModel):
    email: EmailStr
    password: str

class LoginResponseValidator(BaseModel):
    access_token: str
    user: UserResponseValidator