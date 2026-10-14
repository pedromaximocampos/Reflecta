from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from src.modules.auth.public import UserRole

class UserResponseValidator(BaseModel):
    email: EmailStr
    name: str
    surname: str
    username: str
    role: UserRole
    date_of_birth: date
    avatar_url: Optional[str] = None

class LoginRequestValidator(BaseModel):
    email: EmailStr
    password: str

class LoginResponseValidator(BaseModel):
    access_token: str
    user: UserResponseValidator
