from typing import cast

import pytest

from src.modules.auth.public.email import Email
from src.modules.notification.application.handlers.email_event_handler import EmailEventHandler
from src.modules.notification.application.ports.notifiers.dto import EmailDTO, EmailKind
from src.modules.notification.domain.exceptions.email_notification_errors import PermanentEmailError
from src.modules.notification.domain.value_objects.emails_event_types import EmailsEventType


class EmailNotifierSpy:
    def __init__(self) -> None:
        self.sent: list[EmailDTO] = []

    async def send_email(self, dto: EmailDTO) -> None:
        self.sent.append(dto)


def _payload() -> dict:
    return {
        "raw_code": "abc/+=",
        "username": "Pedro",
        "user_email": "PEDRO@example.com",
        "expires_in": 15,
        "occurred_at": "2026-08-31T12:00:00+00:00",
    }


@pytest.mark.asyncio
async def test_maps_verification_event_to_generic_email_dto() -> None:
    notifier = EmailNotifierSpy()
    handler = EmailEventHandler(notifier, "http://localhost:8000/")

    await handler.handle(EmailsEventType.EMAIL_VERIFICATION_REQUESTED, _payload())

    assert notifier.sent == [
        EmailDTO(
            email=Email("pedro@example.com"),
            username="Pedro",
            link=(
                "http://localhost:8000/auth/verify-email"
                "?code=abc%2F%2B%3D"
            ),
            expires_in_minutes=15,
            kind=EmailKind.VERIFICATION,
        )
    ]


@pytest.mark.asyncio
async def test_maps_password_reset_event_to_same_email_dto() -> None:
    notifier = EmailNotifierSpy()
    handler = EmailEventHandler(notifier, "https://app.reflecta.test")

    await handler.handle(EmailsEventType.EMAIL_PASSWORD_RESET_REQUESTED, _payload())

    assert notifier.sent[0].kind is EmailKind.PASSWORD_RESET
    assert notifier.sent[0].link == (
        "https://app.reflecta.test/auth/reset-password?code=abc%2F%2B%3D"
    )


@pytest.mark.asyncio
async def test_rejects_unsupported_email_event_without_sending() -> None:
    notifier = EmailNotifierSpy()
    handler = EmailEventHandler(notifier, "https://app.reflecta.test")

    with pytest.raises(PermanentEmailError, match="Unsupported email event type"):
        await handler.handle(cast(EmailsEventType, "emails.unknown"), _payload())

    assert notifier.sent == []


@pytest.mark.asyncio
async def test_rejects_invalid_payload_without_exposing_field_values() -> None:
    notifier = EmailNotifierSpy()
    handler = EmailEventHandler(notifier, "https://app.reflecta.test")
    payload = _payload()
    del payload["raw_code"]

    with pytest.raises(PermanentEmailError, match="Invalid email event payload"):
        await handler.handle(EmailsEventType.EMAIL_VERIFICATION_REQUESTED, payload)

    assert notifier.sent == []
