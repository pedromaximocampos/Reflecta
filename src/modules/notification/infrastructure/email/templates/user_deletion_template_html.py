from src.modules.notification.application.ports.notifiers.dto import EmailDTO
from src.modules.notification.application.ports.templates.iemail_html_templates import IEmailHtmlTemplates


class UserDeletionTemplateHTML(IEmailHtmlTemplates):
    @staticmethod
    def get_subject_template(dto: EmailDTO) -> str:
        return f"Confirm account deletion for {dto.username}"

    @staticmethod
    def get_email_template(dto: EmailDTO) -> str:
        return f"""
           <!DOCTYPE html>
           <html lang="en">
           <head>
               <meta charset="UTF-8" />
               <title>Confirm account deletion</title>
           </head>
           <body style="font-family: Arial, sans-serif; background:#f6f7f9; padding: 20px;">
               <table width="100%" cellspacing="0" cellpadding="0"
                      style="max-width: 600px; margin: auto; background: #ffffff;
                             border-radius: 8px; padding: 30px;">
                   <tr>
                       <td style="text-align: center;">
                           <h2 style="color: #333333; margin-bottom: 10px;">
                               Confirm account deletion
                           </h2>
                           <p style="color: #555555; font-size: 15px;">
                               Hello {dto.username}, we received a request to delete your account.
                           </p>
                           <p style="color: #555555; font-size: 15px;">
                               Use the button below to review and confirm this action.
                           </p>
                           <a href="{dto.link}"
                              style="display: inline-block; margin-top: 20px; padding: 12px 24px;
                                     background-color: #b91c1c; color: white; text-decoration: none;
                                     border-radius: 6px; font-size: 16px;">
                               Review account deletion
                           </a>
                           <p style="color: #777777; font-size: 13px; margin-top: 25px;">
                               This link expires in <strong>{dto.expires_in_minutes} minutes</strong>.
                           </p>
                           <p style="color: #aaaaaa; font-size: 12px; margin-top: 30px;">
                               If you did not request this action, ignore this email. Your account
                               will remain active.
                           </p>
                       </td>
                   </tr>
               </table>
           </body>
           </html>
           """
