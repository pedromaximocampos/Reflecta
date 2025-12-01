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

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str

    # Segurança / JWT
    JWT_SECRET: str
    JWT_ALGORITHM: Final[PasswordAlgorithm] = PasswordAlgorithm.HS256

    ACCESS_TOKEN_MINUTES: Final[int] = 15
    REFRESH_TOKEN_DAYS: Final[int] = 30
    EMAIL_VERIFICATION_MINUTES: Final[int] = 15

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    RABBITMQ_EMAIL_EXCHANGE: str = "email_exchange"
    RABBITMQ_EMAIL_VERIFICATION_QUEUE: str = "email_verification_queue"
    RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY: str = "email_verification"

    FRONT_END_DOMAIN: str = "http://localhost:8000"

    APP_NAME: str = "Individuum"

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        extra = "ignore"


    # Helper para URL do banco
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"@{self.POSTGRES_PORT}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}"
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
