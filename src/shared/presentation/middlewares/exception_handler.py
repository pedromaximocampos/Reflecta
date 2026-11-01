import logging
import sys
import traceback

from src.shared.config.settings import get_settings
from src.shared.domain.errors.domain_error import DomainError
from src.shared.presentation.http_types.http_response import HttpResponse

_settings = get_settings()
_logger = logging.getLogger(__name__)

_UNEXPECTED_ERROR_BODY = {
    "errors": [
        {
            "title": "UnexpectedError",
            "status": 500,
            "data": "Não foi possível concluir a solicitação. Tente novamente.",
            "details": None,
        }
    ],
    "meta": {},
}


class ExceptionHandler:
    @staticmethod
    def handle_exception(e: Exception) -> HttpResponse:
        if not isinstance(e, DomainError) or e.status_code >= 500:
            _logger.error(
                "Unhandled exception while processing API request",
                exc_info=(type(e), e, e.__traceback__),
            )
            return HttpResponse(
                status_code=500,
                body=_UNEXPECTED_ERROR_BODY,
            )

        meta = {}
        if _settings.DEBUG:
            _, _, exc_tb = sys.exc_info()
            if exc_tb:
                tb = traceback.extract_tb(exc_tb)
                if tb:
                    filename, lineno, func, text = tb[-1]
                    trace = (
                        f"Erro em {filename}, linha {lineno}, "
                        f"função {func}: {text}"
                    )
                    meta["trace"] = trace
                    meta["raw_error"] = str(e)

        return HttpResponse(
            status_code=e.status_code,
            body={
                "errors": [
                    {
                        "title": e.name,
                        "status": e.status_code,
                        "data": e.message,
                        "details": getattr(e, "details", None),
                    }
                ],
                "meta": meta,
            },
        )
