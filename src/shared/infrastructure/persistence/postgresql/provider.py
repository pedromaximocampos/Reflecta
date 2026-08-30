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
    echo=settings.DEBUG,
)

individuum_mvp_provider = DBConnectionHandler(postgres_settings)