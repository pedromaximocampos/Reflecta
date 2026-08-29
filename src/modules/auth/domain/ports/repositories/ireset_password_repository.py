from datetime import datetime
from typing import Optional, Protocol

from src.modules.auth.domain.entities.reset_password import ResetPassword


class IResetPasswordRepository(Protocol):


    async def find_by_hashed_token(self, raw_token: str) -> Optional[ResetPassword]:
        """ Retrieve a ResetPassword entity by its raw token. """
        ...

    async def update_as_used(self, reset_password: ResetPassword, now: datetime) -> ResetPassword:
        """ Mark the given ResetPassword entity as used. """
        ...

    async def create_new_password_reset(self, reset_password: ResetPassword) -> ResetPassword:
        """ Create a new ResetPassword entity. """
        ...