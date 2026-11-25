from html import escape

from src.modules.notification.application.ports.notifiers.dto import EmailDTO
from src.modules.notification.application.ports.templates.iemail_html_templates import (
    IEmailHtmlTemplates,
)


class AdminInvitationTemplateHTML(IEmailHtmlTemplates):
    @staticmethod
    def get_subject_template(dto: EmailDTO) -> str:
        return "Convite para administrar o Reflecta"

    @staticmethod
    def get_email_template(dto: EmailDTO) -> str:
        username = escape(dto.username)
        link = escape(dto.link, quote=True)
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head><meta charset="UTF-8" /><title>Convite administrativo</title></head>
        <body style="margin:0;background:#f5f5f1;font-family:Arial,sans-serif;color:#172019;">
          <table width="100%" cellspacing="0" cellpadding="0" style="padding:32px 16px;">
            <tr><td>
              <table width="100%" cellspacing="0" cellpadding="0"
                     style="max-width:600px;margin:auto;background:#ffffff;border:1px solid #d9dfd7;border-radius:16px;padding:32px;">
                <tr><td>
                  <p style="margin:0 0 8px;color:#3d5844;font-size:14px;font-weight:700;">Reflecta</p>
                  <h1 style="margin:0 0 18px;font-size:25px;line-height:1.25;">Convite para administrar o Reflecta</h1>
                  <p style="font-size:16px;line-height:1.6;">Olá, {username}.</p>
                  <p style="font-size:16px;line-height:1.6;">
                    Um administrador convidou sua conta para ajudar na curadoria do catálogo,
                    na revisão de passagens e no acompanhamento dos processamentos do Reflecta.
                  </p>
                  <p style="font-size:16px;line-height:1.6;">
                    Para proteger sua conta, entre com o mesmo e-mail que recebeu este convite
                    e confirme a alteração de acesso.
                  </p>
                  <p style="margin:28px 0;">
                    <a href="{link}" style="display:inline-block;background:#354c3a;color:#ffffff;text-decoration:none;padding:13px 22px;border-radius:9px;font-weight:700;">
                      Revisar e aceitar convite
                    </a>
                  </p>
                  <p style="font-size:14px;line-height:1.5;color:#68736b;">
                    Este convite expira em {dto.expires_in_minutes // 60} horas e pode ser usado uma única vez.
                  </p>
                  <p style="font-size:13px;line-height:1.5;color:#7f8981;border-top:1px solid #e3e7e2;padding-top:18px;margin-top:24px;">
                    Se você não reconhece este convite, ignore esta mensagem. Nenhuma permissão será alterada sem sua confirmação autenticada.
                  </p>
                </td></tr>
              </table>
            </td></tr>
          </table>
        </body>
        </html>
        """
