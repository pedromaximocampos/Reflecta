from collections.abc import Mapping
from typing import Any, Final
from urllib.parse import urlencode

from src.modules.notification.application.ports.handlers.iemail_event_handler import IEmailEventHandler
from src.modules.notification.domain.value_objects.event_types import EventType
from src.modules.auth.public.email import Email
from src.modules.notification.application.ports.notifiers.dto import EmailDTO, EmailKind
from src.modules.notification.application.ports.notifiers.iemail_notifier import IEmailNotifier
from src.modules.notification.domain.exceptions.email_notification_errors import PermanentEmailError


class EmailEventHandler(IEmailEventHandler):
    _EVENT_CONFIG: Final[dict[EventType, tuple[EmailKind, str]]] = {
        EventType.EMAIL_VERIFICATION_REQUESTED: (
            EmailKind.VERIFICATION,
            "/auth/verify-email",
        ),
        EventType.EMAIL_PASSWORD_RESET_REQUESTED: (
            EmailKind.PASSWORD_RESET,
            "/auth/reset-password",
        ),
    }

    def __init__(
        self,
        email_notifier: IEmailNotifier,
        frontend_base_url: str,
    ) -> None:
        self.__email_notifier = email_notifier
        self.__frontend_base_url = frontend_base_url.rstrip("/")

    async def handle(self, event_type: EventType, payload: Mapping[str, Any]) -> None:
        event_config = self._EVENT_CONFIG.get(event_type)
        if event_config is None:
            raise PermanentEmailError("Unsupported email event type")

        kind, path = event_config
        dto = self.__to_email_dto(payload=payload, kind=kind, path=path)
        await self.__email_notifier.send_email(dto)

    def __to_email_dto(
        self,
        payload: Mapping[str, Any],
        kind: EmailKind,
        path: str,
    ) -> EmailDTO:
        try:
            raw_code = self.__required_string(payload, "raw_code")
            username = self.__required_string(payload, "username")
            user_email = self.__required_string(payload, "user_email")
            expires_in_minutes = int(payload["expires_in"])
            if expires_in_minutes <= 0:
                raise ValueError("expires_in must be positive")

            link = (
                f"{self.__frontend_base_url}{path}?"
                f"{urlencode({'code': raw_code})}"
            )

            return EmailDTO(
                email=Email(user_email),
                username=username,
                link=link,
                expires_in_minutes=expires_in_minutes,
                kind=kind,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise PermanentEmailError("Invalid email event payload") from exc

    @staticmethod
    def __required_string(payload: Mapping[str, Any], field: str) -> str:
        value = payload[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return value.strip()
