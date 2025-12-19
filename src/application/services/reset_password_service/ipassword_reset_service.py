from typing import Protocol

from src.domain.entities.reset_password import ResetPassword
from src.domain.entities.user import User


class IPasswordResetService(Protocol):


    async def issue_for_user(self, user: User) -> ResetPassword:
        """ Create a new password reset token for the given user.
            Creates a new entity to be associated with the user and returns the created entity along with the raw token that should be sent to the user via email.
        """
        ...

