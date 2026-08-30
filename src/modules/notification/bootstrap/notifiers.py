from src.modules.notification.infrastructure.email.smtp.smtp_email_password_reset_notifier import SmtpEmailPasswordResetNotifier
from src.modules.notification.infrastructure.email.smtp.smtp_email_verification_notifier import SMTPEmailVerificationNotifier
from src.modules.notification.bootstrap.providers import get_smtp_provider


def get_email_password_reset_notifier() -> SmtpEmailPasswordResetNotifier:
    """ Retorna a implementação do notificador de verificação de email. """

    return SmtpEmailPasswordResetNotifier(
        smtp_config=get_smtp_provider()
    )


def get_email_verification_notifier() -> SMTPEmailVerificationNotifier:
    """ Retorna a implementação do notificador de verificação de email. """

    return SMTPEmailVerificationNotifier(
        smtp_config=get_smtp_provider()
    )