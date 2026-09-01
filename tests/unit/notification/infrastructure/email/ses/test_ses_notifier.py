from typing import Any

import pytest

from src.modules.auth.public.email import Email
from src.modules.notification.application.ports.notifiers.dto import EmailDTO, EmailKind
from src.modules.notification.infrastructure.email.ses.ses_notifier import SESNotifier


class FakeSESV2Client:
    def __init__(self) -> None:
        self.request: dict[str, Any] | None = None

    def send_email(self, **kwargs: Any) -> dict[str, str]:
        self.request = kwargs
        return {"MessageId": "ses-message-id"}


def _dto(kind: EmailKind, link: str) -> EmailDTO:
    return EmailDTO(
        email=Email("user@example.com"),
        username="Pedro",
        link=link,
        expires_in_minutes=15,
        kind=kind,
    )


@pytest.mark.asyncio
async def test_sends_verification_email_as_simple_html_content() -> None:
    client = FakeSESV2Client()
    notifier = SESNotifier(client, "sender@example.com")
    dto = _dto(
        EmailKind.VERIFICATION,
        "https://app.reflecta.test/auth/verify-email?code=verification-code",
    )

    await notifier.send_email(dto)

    assert client.request is not None
    assert client.request["FromEmailAddress"] == "sender@example.com"
    assert client.request["Destination"] == {"ToAddresses": ["user@example.com"]}
    simple_content = client.request["Content"]["Simple"]
    assert simple_content["Subject"] == {
        "Data": "Verify your email for Pedro",
        "Charset": "UTF-8",
    }
    assert dto.link in simple_content["Body"]["Html"]["Data"]
    assert simple_content["Body"]["Html"]["Charset"] == "UTF-8"


@pytest.mark.asyncio
async def test_sends_password_reset_email_using_existing_template() -> None:
    client = FakeSESV2Client()
    notifier = SESNotifier(client, "sender@example.com")
    dto = _dto(
        EmailKind.PASSWORD_RESET,
        "https://app.reflecta.test/auth/reset-password?code=reset-code",
    )

    await notifier.send_email(dto)

    assert client.request is not None
    simple_content = client.request["Content"]["Simple"]
    assert simple_content["Subject"]["Data"] == "Reset password link for Pedro"
    assert dto.link in simple_content["Body"]["Html"]["Data"]
