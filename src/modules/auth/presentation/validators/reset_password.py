from pydantic import BaseModel, EmailStr


class ResetPasswordValidator(BaseModel):
    reset_token: str
    new_password: str


class RequestResetPasswordValidator(BaseModel):
    email: EmailStr
