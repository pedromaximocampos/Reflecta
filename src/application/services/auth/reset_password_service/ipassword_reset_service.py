from typing import Protocol
from src.domain.entities.user import User
from src.domain.events.emails.password_reset_requested import PasswordResetRequested
from src.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository


class IPasswordResetService(Protocol):


    async def issue_for_user(self, user: User, reset_password_repository: IResetPasswordRepository) -> PasswordResetRequested:
        """ Create a new password reset token for the given user.
            Creates a new entity to be associated with the user and returns the created entity along with the raw token that should be sent to the user via email.
        """
        ...

