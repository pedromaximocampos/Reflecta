
from src.application.ports.emails.dto import EmailVerificationDTO
from src.application.ports.emails.iemail_verification_notifier import IEmailVerificationNotifier
from src.infra.email.smtp.base_smtp_email_notifier import BaseSMTPEmailNotifier
from email.message import EmailMessage


class SMTPEmailVerificationNotifier(BaseSMTPEmailNotifier, IEmailVerificationNotifier):

    def get_subject(self) -> str:
        return f"Verify your email for {self._config.app_name}"


    def get_template(self, dto: EmailVerificationDTO) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>Verify your email</title>
        </head>
        <body style="font-family: Arial, sans-serif; background:#f6f7f9; padding: 20px;">

            <table width="100%" cellspacing="0" cellpadding="0"
                   style="max-width: 600px; margin: auto; background: #ffffff;
                          border-radius: 8px; padding: 30px;">
                <tr>
                    <td style="text-align: center;">
                        <h2 style="color: #333333; margin-bottom: 10px;">
                            Confirm your email address
                        </h2>

                        <p style="color: #555555; font-size: 15px;">
                            Hello {dto.username}, thank you for creating an account!
                        </p>

                        <p style="color: #555555; font-size: 15px;">
                            To complete your registration, please click the button below
                            to verify your email address:
                        </p>

                        <a href="{dto.verification_link}"
                           style="display: inline-block;
                                  margin-top: 20px;
                                  padding: 12px 24px;
                                  background-color: #4f46e5;
                                  color: white;
                                  text-decoration: none;
                                  border-radius: 6px;
                                  font-size: 16px;">
                            Verify email
                        </a>

                        <p style="color: #777777; font-size: 13px; margin-top: 25px;">
                            This link expires in <strong>{dto.expires_in_minutes} minutes</strong>.
                        </p>

                        <p style="color: #aaaaaa; font-size: 12px; margin-top: 30px;">
                            If you did not create an account, you can safely ignore this email.
                        </p>
                    </td>
                </tr>
            </table>

        </body>
        </html>
        """

    async def send_email(self, dto: EmailVerificationDTO) -> None:
        message = EmailMessage()
        message["From"] = self._config.from_address
        message["To"] = dto.email.value
        message["Subject"] = self.get_subject()
        message.set_content(self.get_template(dto), subtype="html")

        await self._send(message)

