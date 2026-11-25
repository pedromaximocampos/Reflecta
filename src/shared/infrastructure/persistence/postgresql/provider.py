from src.shared.config.settings import get_settings
from src.shared.infrastructure.persistence.postgresql.configs.settings import PostgresqlSettings
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler

settings = get_settings()

postgres_settings = PostgresqlSettings(
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    db_name=settings.POSTGRES_DB,
    ssl=(settings.ENV == "prod"),
    echo=settings.SQL_ECHO,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_timeout_seconds=settings.POSTGRES_POOL_TIMEOUT_SECONDS,
    pool_recycle_seconds=settings.POSTGRES_POOL_RECYCLE_SECONDS,
    command_timeout_seconds=settings.POSTGRES_COMMAND_TIMEOUT_SECONDS,
)

individuum_mvp_provider = DBConnectionHandler(postgres_settings)
