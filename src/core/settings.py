# src/core/settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.domain.value_objects.password_algorithm import PasswordAlgorithm
from typing import Final
import os

class Settings(BaseSettings):
    # Ambiente
    ENV: str = "dev"              # dev | prod | test
    DEBUG: bool = True

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Alembic
    ALEMBIC_CONNECTION_STRING: str
    ALEMBIC_MIGRATE: bool = False

    # Segurança / JWT
    JWT_SECRET: str
    JWT_ALGORITHM: Final[PasswordAlgorithm] = PasswordAlgorithm.HS256

    ACCESS_TOKEN_MINUTES: Final[int] = 15
    REFRESH_TOKEN_DAYS: Final[int] = 30

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"


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
    env = os.getenv("ENV", "dev")

    env_file_map = {
        "dev": ".env.dev",
        "test": ".env.test",
        "prod": ".env.prod",
    }

    env_file = env_file_map.get(env, ".env.dev")

    return Settings(_env_file=env_file)
