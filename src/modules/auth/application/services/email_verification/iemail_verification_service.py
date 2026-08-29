from typing import Protocol, Optional

from src.modules.auth.domain.entities.email_verification import EmailVerification
from src.modules.auth.domain.entities.user import User
from src.modules.auth.domain.events.emails.verification_requested import EmailVerificationRequested
from src.modules.auth.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork


class IEmailVerificationService(Protocol):

    async def create_email_verification_event(self, user: User, user_email_repo: IUserEmailVerificationRepository) -> EmailVerificationRequested:
        """ Cria uma novo evento verificação de email para o usuário fornecido e salva no repositorio de email verificação.
        """
        ...

    async def ensure_or_issue(self, user: User, repo: IUserEmailVerificationRepository) -> Optional[EmailVerificationRequested]:
        """
       Search for a valid email verification for the user. If none exists or if the existing one is expired, create a new one and return the corresponding event.
       If returns None, it means there is already a valid verification in place, requesting a validation.
        """
        ...