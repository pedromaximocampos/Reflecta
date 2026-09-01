from enum import StrEnum


class EmailsEventType(StrEnum):
    EMAIL_VERIFICATION_REQUESTED = "emails.verification.requested"
    EMAIL_PASSWORD_RESET_REQUESTED = "emails.password_reset.requested"
