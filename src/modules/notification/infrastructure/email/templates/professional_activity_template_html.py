from html import escape

from src.modules.notification.application.ports.notifiers.dto import (
    EmailActivityDTO,
    EmailDTO,
)
from src.modules.notification.application.ports.templates.iemail_html_templates import (
    IEmailHtmlTemplates,
)


class ProfessionalActivityTemplateHTML(IEmailHtmlTemplates):
    @staticmethod
    def get_subject_template(dto: EmailDTO) -> str:
        if len(dto.activities) > 1:
            return f"Você recebeu {len(dto.activities)} novas orientações no Reflecta"
        activity = dto.activities[0]
        label = (
            "reflexão guiada"
            if activity.activity_type == "guided_reflection"
            else "atividade"
        )
        return f"Você recebeu uma nova {label} no Reflecta"

    @staticmethod
    def get_email_template(dto: EmailDTO) -> str:
        cards = "".join(
            ProfessionalActivityTemplateHTML._activity_card(activity)
            for activity in dto.activities
        )
        return f"""
        <!doctype html>
        <html lang="pt-BR">
          <body style="margin:0;background:#f5f4ef;color:#20241f;font-family:Arial,sans-serif;">
            <div style="max-width:620px;margin:0 auto;padding:32px 20px;">
              <div style="background:#ffffff;border:1px solid #d9ddd5;border-radius:16px;padding:28px;">
                <p style="margin:0 0 8px;color:#3f5a43;font-weight:700;">Reflecta</p>
                <h1 style="margin:0 0 18px;font-size:24px;">Nova orientação recebida</h1>
                <p>Olá, {escape(dto.username)}.</p>
                <p>Uma pessoa com acesso à sua análise compartilhada enviou {len(dto.activities)} nova(s) orientação(ões).</p>
                <div style="margin:22px 0;">{cards}</div>
                <a href="{escape(dto.link)}" style="display:inline-block;padding:12px 18px;border-radius:9px;background:#3f5a43;color:#ffffff;text-decoration:none;">Acessar o Reflecta</a>
                <p style="margin:22px 0 0;color:#687068;font-size:13px;">O Reflecta não substitui acompanhamento profissional ou atendimento de emergência.</p>
              </div>
            </div>
          </body>
        </html>
        """.strip()

    @staticmethod
    def _activity_card(activity: EmailActivityDTO) -> str:
        label = (
            "Reflexão guiada"
            if activity.activity_type == "guided_reflection"
            else "Atividade"
        )
        due_date = (
            f"<p style=\"margin:10px 0 0;\"><strong>Prazo sugerido:</strong> {escape(activity.due_date)}</p>"
            if activity.due_date
            else ""
        )
        return f"""
        <div style="margin:0 0 12px;padding:18px;border-left:4px solid #3f5a43;background:#f5f4ef;">
          <p style="margin:0 0 8px;"><strong>{label}:</strong> {escape(activity.activity_title)}</p>
          <p style="margin:0;white-space:pre-line;">{escape(activity.activity_description)}</p>
          {due_date}
        </div>
        """.strip()

