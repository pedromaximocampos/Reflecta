from typing import Protocol

from src.domain.entities.email_verification import EmailVerification
from src.domain.entities.user import User


class IEmailVerificationService(Protocol):

    async def issue_for_user(self, user: User) -> tuple[EmailVerification, str]:
        """ Cria uma nova verificação de email para o usuário fornecido.
            Cria uma nova entidade a ser associada ao usuário e retorna a entidade criada junto com o token bruto que deve ser enviado ao usuário por email.
        """
        ...