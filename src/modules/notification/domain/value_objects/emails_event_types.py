from enum import StrEnum


class EmailsEventType(StrEnum):
    EMAIL_VERIFICATION_REQUESTED = "emails.verification.requested"
    EMAIL_PASSWORD_RESET_REQUESTED = "emails.password_reset.requested"
    EMAIL_USER_DELETION_REQUESTED = "emails.user_deletion.requested"
    EMAIL_USER_RECOVERY_REQUESTED = "emails.recovery_user.requested"
