# main/composables/core/systems.py

from src.infra.system.system_clock import SystemClock
from src.infra.system.ulid_generator import UlidGenerator
from src.infra.system.jti_hasher import JTIHasher

# Criados uma única vez – Singleton no nível de módulo
_clock = SystemClock()
_ulid_generator = UlidGenerator()
_jti_hasher = JTIHasher()


def get_clock() -> SystemClock:
    """
    Retorna uma instância única de SystemClock para ser usada pelo sistema todo.
    """
    return _clock


def get_ulid_generator() -> UlidGenerator:
    """
    Retorna um gerador de ULID usado em criação de IDs de entidades.
    """
    return _ulid_generator


def get_jti_hasher() -> JTIHasher:
    """
    Retorna o hasher de JTI usado para hashing do jti sem guardar em texto puro.
    """
    return _jti_hasher
