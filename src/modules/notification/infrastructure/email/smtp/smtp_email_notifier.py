from email.message import EmailMessage

from src.modules.notification.infrastructure.email.templates.password_reset_template_html import PasswordResetTemplateHTML
from src.modules.notification.infrastructure.email.templates.verification_template_html import VerificationTemplateHTML
from src.modules.notification.infrastructure.email.templates.user_deletion_template_html import UserDeletionTemplateHTML
from src.modules.notification.infrastructure.email.templates.user_recovery_template_html import UserRecoveryTemplateHTML
from src.modules.notification.application.ports.notifiers.dto import EmailDTO, EmailKind
from src.modules.notification.application.ports.notifiers.iemail_notifier import IEmailNotifier
from src.modules.notification.infrastructure.email.smtp.base_smtp_email_notifier import BaseSMTPEmailNotifier


class SMTPEmailNotifier(BaseSMTPEmailNotifier, IEmailNotifier):
    def get_subject(self, dto: EmailDTO) -> str:
        if dto.kind is EmailKind.VERIFICATION:
            return f"Verify your email for {self._config.app_name}"
        if dto.kind is EmailKind.PASSWORD_RESET:
            return f"Reset password link for {self._config.app_name}"
        if dto.kind is EmailKind.USER_DELETION:
            return f"Confirm account deletion for {self._config.app_name}"
        if dto.kind is EmailKind.USER_RECOVERY:
            return f"Recover your account for {self._config.app_name}"
        raise ValueError(f"Unsupported email kind: {dto.kind}")

    def get_template(self, dto: EmailDTO) -> str:
        if dto.kind is EmailKind.VERIFICATION:
            return VerificationTemplateHTML.get_email_template(dto)
        if dto.kind is EmailKind.PASSWORD_RESET:
            return PasswordResetTemplateHTML.get_email_template(dto)
        if dto.kind is EmailKind.USER_DELETION:
            return UserDeletionTemplateHTML.get_email_template(dto)
        if dto.kind is EmailKind.USER_RECOVERY:
            return UserRecoveryTemplateHTML.get_email_template(dto)
        raise ValueError(f"Unsupported email kind: {dto.kind}")

    async def send_email(self, dto: EmailDTO) -> None:
        message = EmailMessage()
        message["From"] = self._config.from_address
        message["To"] = dto.email.value
        message["Subject"] = self.get_subject(dto)
        message.set_content(self.get_template(dto), subtype="html")

        await self._send(message)
