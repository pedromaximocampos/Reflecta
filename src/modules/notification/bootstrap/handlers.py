from src.modules.notification.application.handlers.email_event_handler import EmailEventHandler
from src.modules.notification.bootstrap.notifiers import get_email_notifier
from src.modules.notification.bootstrap.providers import get_frontend_base_url


def get_email_event_handler() -> EmailEventHandler:
    return EmailEventHandler(
        email_notifier=get_email_notifier(),
        frontend_base_url=get_frontend_base_url(),
    )
