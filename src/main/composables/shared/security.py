from src.infra.security.argon2id_password_hasher import Argon2IdPasswordHasher
from src.infra.security.token_service import TokenServiceImpl
from src.core.settings import get_settings

_settings = get_settings()

# Criados uma vez — usados pelo o sistema
_password_hasher = Argon2IdPasswordHasher()
_token_service = TokenServiceImpl(_settings.JWT_SECRET)


def get_password_hasher() -> Argon2IdPasswordHasher:
    """
    Retorna o hasher de senha Argon2 para ser usado em qualquer contexto que precise validar senha.
    """
    return _password_hasher


def get_token_service() -> TokenServiceImpl:
    """
    Serviço de geração/validação de token JWT compartilhado entre use cases.
    """
    return _token_service
