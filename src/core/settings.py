# src/core/settings.py
from functools import lru_cache
from pydantic import BaseSettings
from src.domain.value_objects.password_algorithm import PasswordAlgorithm
from typing import Final

class Settings(BaseSettings):
    # Ambiente
    env: str = "dev"              # dev | prod | test
    debug: bool = True

    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # Alembic
    alembic_connection_string: str
    alembic_migrate: bool = False

    # Segurança / JWT
    jwt_secret: str
    jwt_algorithm: PasswordAlgorithm  = PasswordAlgorithm.HS256
    access_token_minutes: Final[int] = 15
    refresh_token_days: Final[int] = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


    # Helper para URL do banco
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Retorna uma instância única de Settings (singleton via cache).
    """
    return Settings()
