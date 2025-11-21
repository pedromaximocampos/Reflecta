from src.core.settings import get_settings
from src.infra.postgresql.configs.settings import PostgresqlSettings
from src.infra.postgresql.connection import DBConnectionHandler

settings = get_settings()

postgres_settings = PostgresqlSettings(
    user=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    db_name=settings.postgres_db,
    ssl=(settings.env == "prod"),
    echo=settings.debug,
)

individuum_mvp_provider = DBConnectionHandler(postgres_settings)