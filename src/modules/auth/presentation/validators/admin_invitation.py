from pydantic import BaseModel, Field


class CreateAdminInvitationValidator(BaseModel):
    email: str = Field(min_length=3, max_length=255)
