from src.modules.notification.bootstrap.providers import get_smtp_provider
from src.modules.notification.infrastructure.email.smtp.smtp_email_notifier import SMTPEmailNotifier


def get_email_notifier() -> SMTPEmailNotifier:
    return SMTPEmailNotifier(
        smtp_config=get_smtp_provider()
    )
