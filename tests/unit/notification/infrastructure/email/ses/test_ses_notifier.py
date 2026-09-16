import logging
from typing import Any

import pytest
from botocore.exceptions import ClientError

from src.modules.notification.application.ports.notifiers.dto import EmailDTO, EmailKind
from src.modules.notification.domain.exceptions.email_notification_errors import (
    PermanentEmailError,
)
from src.modules.notification.domain.value_objects.recipient_email import RecipientEmail
from src.modules.notification.infrastructure.email.ses.ses_notifier import SESNotifier


class FakeSESV2Client:
    def __init__(self) -> None:
        self.request: dict[str, Any] | None = None

    def send_email(self, **kwargs: Any) -> dict[str, str]:
        self.request = kwargs
        return {"MessageId": "ses-message-id"}


class RejectingSESV2Client:
    def send_email(self, **kwargs: Any) -> dict[str, str]:
        raise ClientError(
            error_response={
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "Not authorized to send to user@example.com",
                },
                "ResponseMetadata": {
                    "RequestId": "ses-request-id",
                    "HTTPStatusCode": 403,
                },
            },
            operation_name="SendEmail",
        )


def _dto(kind: EmailKind, link: str) -> EmailDTO:
    return EmailDTO(
        email=RecipientEmail("user@example.com"),
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


@pytest.mark.asyncio
async def test_sends_user_deletion_email_using_confirmation_template() -> None:
    client = FakeSESV2Client()
    notifier = SESNotifier(client, "sender@example.com")
    dto = _dto(
        EmailKind.USER_DELETION,
        "https://app.reflecta.test/auth/delete?code=deletion-code",
    )

    await notifier.send_email(dto)

    assert client.request is not None
    simple_content = client.request["Content"]["Simple"]
    assert simple_content["Subject"]["Data"] == "Confirm account deletion for Pedro"
    assert dto.link in simple_content["Body"]["Html"]["Data"]
    assert "will remain active" in simple_content["Body"]["Html"]["Data"]


@pytest.mark.asyncio
async def test_sends_user_recovery_email_using_confirmation_template() -> None:
    client = FakeSESV2Client()
    notifier = SESNotifier(client, "sender@example.com")
    dto = _dto(
        EmailKind.USER_RECOVERY,
        "https://app.reflecta.test/auth/recovery?code=recovery-code",
    )

    await notifier.send_email(dto)

    assert client.request is not None
    simple_content = client.request["Content"]["Simple"]
    assert simple_content["Subject"]["Data"] == "Recover your account for Pedro"
    assert dto.link in simple_content["Body"]["Html"]["Data"]
    assert "will remain deleted" in simple_content["Body"]["Html"]["Data"]


@pytest.mark.asyncio
async def test_logs_safe_ses_diagnostics_without_email_or_aws_message(caplog) -> None:
    notifier = SESNotifier(RejectingSESV2Client(), "sender@example.com")
    dto = _dto(
        EmailKind.VERIFICATION,
        "https://app.reflecta.test/auth/verify-email?code=secret-code",
    )

    with caplog.at_level(
        logging.ERROR,
        logger="src.modules.notification.infrastructure.email.ses.ses_notifier",
    ):
        with pytest.raises(PermanentEmailError):
            await notifier.send_email(dto)

    log_output = caplog.text
    assert "error_code=AccessDeniedException" in log_output
    assert "http_status=403" in log_output
    assert "request_id=ses-request-id" in log_output
    assert "user@example.com" not in log_output
    assert "sender@example.com" not in log_output
    assert "secret-code" not in log_output
    assert "Not authorized" not in log_output
