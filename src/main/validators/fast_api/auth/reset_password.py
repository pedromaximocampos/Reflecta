from pydantic import BaseModel


class ResetPasswordValidator(BaseModel):
    reset_token: str
    new_password: str


