from src.shared.infrastructure.system.slug_generator import SlugGenerator
from src.shared.infrastructure.system.system_clock import SystemClock
from src.shared.infrastructure.system.ulid_generator import UlidGenerator

# Criados uma única vez – Singleton no nível de módulo
_clock = SystemClock()
_slug_generator = SlugGenerator()
_ulid_generator = UlidGenerator()


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


def get_slug_generator() -> SlugGenerator:
    """Retorna o gerador de slugs determinístico usado pela aplicação."""
    return _slug_generator
