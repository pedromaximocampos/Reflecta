from collections.abc import Mapping
from typing import Any, Final
from urllib.parse import urlencode

from src.modules.notification.application.ports.handlers.iemail_event_handler import IEmailEventHandler
from src.modules.notification.domain.value_objects.emails_event_types import EmailsEventType
from src.modules.notification.application.ports.notifiers.dto import (
    EmailActivityDTO,
    EmailDTO,
    EmailKind,
)
from src.modules.notification.application.ports.notifiers.iemail_notifier import IEmailNotifier
from src.modules.notification.domain.exceptions.email_notification_errors import PermanentEmailError
from src.modules.notification.domain.value_objects.recipient_email import RecipientEmail


class EmailEventHandler(IEmailEventHandler):
    _EVENT_CONFIG: Final[dict[EmailsEventType, tuple[EmailKind, str]]] = {
        EmailsEventType.EMAIL_VERIFICATION_REQUESTED: (
            EmailKind.VERIFICATION,
            "/auth/verify-email",
        ),
        EmailsEventType.EMAIL_PASSWORD_RESET_REQUESTED: (
            EmailKind.PASSWORD_RESET,
            "/auth/reset-password",
        ),
        EmailsEventType.EMAIL_USER_DELETION_REQUESTED: (
            EmailKind.USER_DELETION,
            "/auth/delete",
        ),
        EmailsEventType.EMAIL_USER_RECOVERY_REQUESTED: (
            EmailKind.USER_RECOVERY,
            "/auth/recovery",
        ),
        EmailsEventType.EMAIL_PROFESSIONAL_ACTIVITIES_ASSIGNED: (
            EmailKind.PROFESSIONAL_ACTIVITY,
            "/inicio/orientacoes",
        ),
        EmailsEventType.EMAIL_ADMIN_INVITATION_REQUESTED: (
            EmailKind.ADMIN_INVITATION,
            "/auth/admin-invitation",
        ),
    }

    def __init__(
        self,
        email_notifier: IEmailNotifier,
        frontend_base_url: str,
    ) -> None:
        self.__email_notifier = email_notifier
        self.__frontend_base_url = frontend_base_url.rstrip("/")

    async def handle(self, event_type: EmailsEventType, payload: Mapping[str, Any]) -> None:
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
            username = self.__required_string(payload, "username")
            user_email = self.__required_string(payload, "user_email")
            if kind is EmailKind.PROFESSIONAL_ACTIVITY:
                raw_activities = payload["activities"]
                if (
                    not isinstance(raw_activities, list)
                    or not 1 <= len(raw_activities) <= 20
                ):
                    raise ValueError("activities must contain between 1 and 20 items")
                activities = tuple(
                    self.__to_activity_dto(item)
                    for item in raw_activities
                )
                return EmailDTO(
                    email=RecipientEmail(user_email),
                    username=username,
                    link=f"{self.__frontend_base_url}{path}",
                    expires_in_minutes=0,
                    kind=kind,
                    activities=activities,
                )

            raw_code = self.__required_string(payload, "raw_code")
            expires_in_minutes = int(payload["expires_in"])
            if expires_in_minutes <= 0:
                raise ValueError("expires_in must be positive")

            link = (
                f"{self.__frontend_base_url}{path}?"
                f"{urlencode({'code': raw_code})}"
            )

            return EmailDTO(
                email=RecipientEmail(user_email),
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

    @classmethod
    def __to_activity_dto(cls, value: Any) -> EmailActivityDTO:
        if not isinstance(value, Mapping):
            raise ValueError("activity must be an object")
        activity_type = cls.__required_string(value, "activity_kind")
        if activity_type not in {"activity", "guided_reflection"}:
            raise ValueError("invalid activity_kind")
        due_date = value.get("due_date")
        if due_date is not None and not isinstance(due_date, str):
            raise ValueError("due_date must be a string or null")
        return EmailActivityDTO(
            activity_type=activity_type,
            activity_title=cls.__required_string(value, "title"),
            activity_description=cls.__required_string(value, "description"),
            due_date=due_date,
        )
