from src.modules.auth.public.email import Email
from src.modules.notification.application.ports.notifiers.dto import EmailDTO, EmailKind
from src.modules.notification.infrastructure.email.smtp.configs.settings import SMTPSettings
from src.modules.notification.infrastructure.email.smtp.smtp_email_notifier import SMTPEmailNotifier


def _notifier() -> SMTPEmailNotifier:
    return SMTPEmailNotifier(
        SMTPSettings(
            server="smtp.example.com",
            port=587,
            username="sender@example.com",
            password="not-used",
            frontend_domain="https://app.reflecta.test",
            app_name="Reflecta",
            use_ssl=False,
        )
    )


def _dto(kind: EmailKind, link: str) -> EmailDTO:
    return EmailDTO(
        email=Email("user@example.com"),
        username="Pedro",
        link=link,
        expires_in_minutes=15,
        kind=kind,
    )


def test_renders_verification_email_from_generic_dto() -> None:
    notifier = _notifier()
    dto = _dto(
        EmailKind.VERIFICATION,
        "https://app.reflecta.test/auth/verify-email?code=verification-code",
    )

    assert notifier.get_subject(dto) == "Verify your email for Reflecta"
    assert dto.link in notifier.get_template(dto)
    assert "Verify email" in notifier.get_template(dto)


def test_renders_password_reset_email_from_same_generic_dto() -> None:
    notifier = _notifier()
    dto = _dto(
        EmailKind.PASSWORD_RESET,
        "https://app.reflecta.test/auth/reset-password?code=reset-code",
    )

    assert notifier.get_subject(dto) == "Reset password link for Reflecta"
    assert dto.link in notifier.get_template(dto)
    assert "Reset password" in notifier.get_template(dto)
