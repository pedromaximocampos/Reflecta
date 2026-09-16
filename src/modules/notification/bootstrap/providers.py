from src.shared.config.settings import get_settings
from src.modules.notification.infrastructure.email.smtp.configs.settings import SMTPSettings

_settings = get_settings()


def get_smtp_provider() -> SMTPSettings:
    smtp_settings = SMTPSettings(
        server=_settings.SMTP_HOST,
        port=_settings.SMTP_PORT,
        username=_settings.SMTP_USER,
        password=_settings.SMTP_PASSWORD,
        frontend_domain=_settings.FRONT_END_DOMAIN,
        app_name=_settings.APP_NAME,
        use_ssl=(_settings.ENV == "prod"),
    )

    return smtp_settings


def get_frontend_base_url() -> str:
    return _settings.FRONT_END_DOMAIN

