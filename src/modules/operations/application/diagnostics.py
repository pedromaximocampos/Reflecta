"""Read-time allowlist: stored/provider messages are never API response fields."""
import json
from src.modules.ai_processing.application.failure_reasons import FailureReason

MESSAGES = {reason.value: reason.message for reason in FailureReason}
MESSAGES.update({
    "WorkIngestionProcessingStorageError": "Falha ao acessar o armazenamento do documento.",
    "WorkDocumentExtractionError": "Não foi possível extrair o texto do documento.",
    "WorkDocumentNormalizationError": "Não foi possível normalizar o texto do documento.",
    "WorkDocumentChunkingError": "Não foi possível dividir o documento em trechos.",
    "WorkIngestionProcessingError": "Falha no processamento da obra.",
    "WorkPassageAnalysisError": "Falha na análise de passagens da obra.",
    "InboxClaimLostError": "O processamento perdeu a reserva do evento recebido.",
    "storage_error": "Falha ao acessar o armazenamento do documento.",
    "document_extraction_failed": "Não foi possível extrair o texto do documento.",
    "document_normalization_failed": "Não foi possível normalizar o texto do documento.",
    "document_chunking_failed": "Não foi possível dividir o documento em trechos.",
    "work_passage_analysis_failed": "Falha na análise de passagens da obra.",
    "event_delivery_failed": "Não foi possível entregar o evento interno.",
    "aws_credentials_unavailable": "As credenciais AWS do publicador estão indisponíveis ou expiraram.",
    "aws_access_denied": "A AWS recusou a entrega do evento por falta de permissão.",
    "event_provider_unreachable": "Não foi possível conectar ao serviço de mensageria.",
})
UNKNOWN = {"code": "unknown_error", "message": "Motivo detalhado indisponível."}


def safe_diagnostic(*, raw=None, code=None, attempts=None):
    if raw is not None:
        try:
            saved = json.loads(raw)
            if isinstance(saved, dict):
                code = saved.get("code")
                attempts = saved.get("attempts")
        except (ValueError, TypeError):
            pass
    diagnostic = {"code": code, "message": MESSAGES[code]} if isinstance(code, str) and code in MESSAGES else dict(UNKNOWN)
    diagnostic["attempts"] = attempts if type(attempts) is int and 0 <= attempts <= 1000000 else None
    return diagnostic


def safe_outbox_diagnostic(*, raw=None, attempts=None):
    """Classify delivery failures without returning provider exception text."""
    normalized = raw.lower() if isinstance(raw, str) else ""
    if any(marker in normalized for marker in (
        "unable to locate credentials",
        "unable to load credentials",
        "credential provider",
        "credentials failed",
        "expiredtoken",
        "token has expired",
        "refresh token has expired",
        "error loading sso token",
        "sso token",
        "login session",
    )):
        code = "aws_credentials_unavailable"
    elif any(marker in normalized for marker in (
        "accessdenied",
        "access denied",
        "not authorized to perform",
        "authorizationerror",
    )):
        code = "aws_access_denied"
    elif any(marker in normalized for marker in (
        "endpointconnectionerror",
        "could not connect to the endpoint",
        "connect timeout",
        "connection timed out",
        "name resolution",
    )):
        code = "event_provider_unreachable"
    else:
        code = "event_delivery_failed"
    return safe_diagnostic(code=code, attempts=attempts)
