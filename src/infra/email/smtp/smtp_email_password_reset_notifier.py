from email.message import EmailMessage
from typing import Any

from src.application.ports.emails.dto import EmailPasswordResetDTO
from src.application.ports.emails.iemail_password_reset_notifier import IEmailPasswordResetNotifier
from src.infra.email.smtp.base_smtp_email_notifier import BaseSMTPEmailNotifier


class SmtpEmailPasswordResetNotifier(BaseSMTPEmailNotifier, IEmailPasswordResetNotifier):

    def get_subject(self) -> str:
        return f"Reset password link for {self._config.app_name}"

    def get_template(self, dto: EmailPasswordResetDTO) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>Reset your password</title>
        </head>
        <body style="font-family: Arial, sans-serif; background:#f6f7f9; padding: 20px;">

            <table width="100%" cellspacing="0" cellpadding="0"
                   style="max-width: 600px; margin: auto; background: #ffffff;
                          border-radius: 8px; padding: 30px;">
                <tr>
                    <td style="text-align: center;">
                        <h2 style="color: #333333; margin-bottom: 10px;">
                            Reset your password
                        </h2>

                        <p style="color: #555555; font-size: 15px;">
                            Hello {dto.user_name},
                        </p>

                        <p style="color: #555555; font-size: 15px;">
                            We received a request to reset the password associated with
                            your account ({dto.email.value}).
                        </p>

                        <p style="color: #555555; font-size: 15px;">
                            Click the button below to create a new password:
                        </p>

                        <a href="{dto.reset_password_link}"
                           style="display: inline-block;
                                  margin-top: 20px;
                                  padding: 12px 24px;
                                  background-color: #4f46e5;
                                  color: white;
                                  text-decoration: none;
                                  border-radius: 6px;
                                  font-size: 16px;">
                            Reset password
                        </a>

                        <p style="color: #777777; font-size: 13px; margin-top: 25px;">
                            This link expires in <strong>{dto.expires_in_minutes} minutes</strong>.
                        </p>

                        <p style="color: #aaaaaa; font-size: 12px; margin-top: 30px;">
                            If you did not request a password reset, you can safely ignore
                            this email. Your password will remain unchanged.
                        </p>
                    </td>
                </tr>
            </table>

        </body>
        </html>
        """

    async def send_email(self, email_password_reset_dto: EmailPasswordResetDTO) -> None:
        message =  EmailMessage()
        message["Subject"] = self.get_subject()
        message["From"] = self._config.from_address
        message["To"] = email_password_reset_dto.email.value
        message.set_content(
            self.get_template(email_password_reset_dto),
            subtype="html"
        )
        await self._send(message)
