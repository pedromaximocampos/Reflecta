from pydantic import BaseModel, EmailStr


class RequestRecoveryValidator(BaseModel):
    email: EmailStr
