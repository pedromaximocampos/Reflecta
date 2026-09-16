from src.modules.notification.application.ports.notifiers.dto import EmailDTO
from src.modules.notification.application.ports.templates.iemail_html_templates import IEmailHtmlTemplates


class VerificationTemplateHTML(IEmailHtmlTemplates):

    @staticmethod
    def get_subject_template(dto: EmailDTO) -> str:
        return f"Verify your email for {dto.username}"

    @staticmethod
    def get_email_template(dto: EmailDTO) -> str:
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

                           <a href="{dto.link}"
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
