from src.core.settings import get_settings
from src.modules.notification.infrastructure.email.smtp.configs.settings import SMTPSettings
from src.infra.postgresql.configs.settings import PostgresqlSettings
from src.infra.postgresql.connection import DBConnectionHandler

settings = get_settings()


def get_postgresql_provider() -> DBConnectionHandler:

    postgres_settings = PostgresqlSettings(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        db_name=settings.POSTGRES_DB,
        ssl=(settings.ENV == "prod"),
        echo=settings.DEBUG,
    )

    return DBConnectionHandler(postgres_settings)


def get_smtp_provider() -> SMTPSettings:
    smtp_settings = SMTPSettings(
        server=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        frontend_domain=settings.FRONT_END_DOMAIN,
        app_name=settings.APP_NAME,
        use_ssl=(settings.ENV == "prod"),
    )

    return smtp_settings

