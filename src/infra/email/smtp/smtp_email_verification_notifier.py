
from src.application.ports.emails.dto import EmailVerificationDTO
from src.infra.email.smtp.base_smtp_email_notifier import BaseSMTPEmailNotifier
from email.message import EmailMessage


class SMTPEmailVerificationNotifier(BaseSMTPEmailNotifier):

    def get_subject(self) -> str:
        return f"Verifique seu e-mail para {self._app_name}"


    def get_template(self, dto: EmailVerificationDTO) -> str:
        return  f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8" />
            <title>Verifique seu e-mail</title>
        </head>
        <body style="font-family: Arial, sans-serif; background:#f6f7f9; padding: 20px;">
        
            <table width="100%" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; padding: 30px;">
                <tr>
                    <td style="text-align: center;">
                        <h2 style="color: #333333; margin-bottom: 10px;">Confirmar endereço de e-mail</h2>
                        <p style="color: #555555; font-size: 15px;">
                            Olá{dto.user_name}, obrigado por criar uma conta no <strong></strong>!
                        </p>
                        <p style="color: #555555; font-size: 15px;">
                            Para concluir seu cadastro, clique no botão abaixo para verificar seu endereço de e-mail:
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
                            Verificar e-mail
                        </a>
        
                        <p style="color: #777777; font-size: 13px; margin-top: 25px;">
                            Este link expira em <strong>{dto.expires_in_minutes} minutos</strong>.
                        </p>
        
                        <p style="color: #aaaaaa; font-size: 12px; margin-top: 30px;">
                            Se você não criou uma conta, apenas ignore este e-mail.
                        </p>
                    </td>
                </tr>
            </table>
        
        </body>
        </html>
        """



    async def send_email(self, dto: EmailVerificationDTO) -> None:
        message = EmailMessage()
        message["From"] = self._from
        message["To"] = dto.email
        message["Subject"] = self.get_subject()
        message.set_content(self.get_template(dto), subtype="html")

        await self._send(message)

