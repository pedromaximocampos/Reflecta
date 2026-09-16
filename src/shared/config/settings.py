# src/core/settings.py
import logging
from functools import lru_cache
from logging.config import dictConfig

from pydantic_settings import BaseSettings
from typing import Final, Optional
import os

class Settings(BaseSettings):
    # Ambiente
    ENV: str = "dev"              # dev | prod | test
    DEBUG: bool = True if ENV == "dev" else False
    SQL_ECHO: bool
    LOG_LEVEL: str = "ERROR"       # DEBUG | INFO | WARNING | ERROR | CRITICAL

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

    MAX_SESSIONS_PER_USER: Final[int] = 5

    # AWS
    AWS_PROFILE: Optional[str] = None

    # AWS-SQS
    AWS_SQS_REGION: Final[str]
    AWS_SQS_EMAILS_QUEUE_URL: Final[str]

    # WORKERS
    BATCH_LIMIT: Final[int]
    ATTEMPTS_LIMIT: Final[int]


    # Segurança / JWT
    JWT_SECRET: str
    JWT_ALGORITHM: Final[str] = "HS256"

    ACCESS_TOKEN_MINUTES: Final[int] = 15
    REFRESH_TOKEN_DAYS: Final[int] = 30
    EMAIL_VERIFICATION_MINUTES: Final[int] = 15
    RESET_PASSWORD_MINUTES: Final[int] = 15
    USER_DELETION_MINUTES: int = 15
    USER_RECOVERY_MINUTES: int = 15

    MINIMUM_PASSWORD_LENGTH: Final[int] = 12

    # RabbitMQ connection
    RABBITMQ_URL: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VIRTUAL_HOST: str
    RABBITMQ_USE_SSL: bool = False

    AWS_SNS_REGION: str
    AWS_SNS_ARN: str



    # Exchanges
    RABBITMQ_EMAIL_EXCHANGE: str
    RABBITMQ_EMAIL_DLX_EXCHANGE: str

    # Email verification
    RABBITMQ_EMAIL_VERIFICATION_QUEUE: str
    RABBITMQ_EMAIL_VERIFICATION_RETRY_QUEUE: str
    RABBITMQ_EMAIL_VERIFICATION_DLX_QUEUE: str

    RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY: str
    RABBITMQ_EMAIL_VERIFICATION_RETRY_ROUTING_KEY: str
    RABBITMQ_EMAIL_VERIFICATION_DLX_ROUTING_KEY: str

    # Password reset
    RABBITMQ_PASSWORD_RESET_QUEUE: str
    RABBITMQ_PASSWORD_RESET_RETRY_QUEUE: str
    RABBITMQ_PASSWORD_RESET_DLX_QUEUE: str

    RABBITMQ_PASSWORD_RESET_ROUTING_KEY: str
    RABBITMQ_PASSWORD_RESET_RETRY_ROUTING_KEY: str
    RABBITMQ_PASSWORD_RESET_DLX_ROUTING_KEY: str

    # Retries
    RABBITMQ_MAX_RETRIES: int = 5

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
        return self.RABBITMQ_URL

    def configure_logging(self) -> None:
        level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
        dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level
            }
        })



@lru_cache
def get_settings() -> Settings:
    """
    Retorna uma instância única de Settings (singleton via cache).
    """
    env = os.getenv("ENV")

    env_file_map = {
        "dev": ".env.dev",
        "test": ".env.test",
        "prod": ".env.prod",
    }

    env_file = env_file_map.get(env)

    settings =  Settings(_env_file=env_file)
    settings.configure_logging()
    return settings
