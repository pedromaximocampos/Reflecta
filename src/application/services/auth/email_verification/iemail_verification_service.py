from typing import Protocol

from src.domain.entities.email_verification import EmailVerification
from src.domain.entities.user import User
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork


class IEmailVerificationService(Protocol):

    async def issue_for_user(self, user: User, uow: IAuthUnitOfWork) -> tuple[EmailVerification, str]:
        """ Cria uma nova verificação de email para o usuário fornecido.
            Cria uma nova entidade a ser associada ao usuário e retorna a entidade criada junto com o token bruto que deve ser enviado ao usuário por email.
        """
        ...

    async def ensure_active_verification_for_user(self, user: User, uow: IAuthUnitOfWork) -> EmailVerification:
        """
        Garante que o usuário tenha uma verificação ativa:
        - se não existir, cria e envia
        - se existir e estiver expirada, revoga, cria e envia
        - se existir e estiver válida, só não faz nada
        """
        ...