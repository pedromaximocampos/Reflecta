from typing import Optional, Protocol

from src.domain.entities.reset_password import ResetPassword


class IResetPasswordRepository(Protocol):


    async def find_by_hashed_token(self, raw_token: str) -> Optional[ResetPassword]:
        """ Retrieve a ResetPassword entity by its raw token. """
        ...