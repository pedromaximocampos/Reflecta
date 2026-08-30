# src/presentation/exception_handler.py
from typing import Tuple, Type
from src.shared.domain.errors.domain_error import DomainError
from src.shared.presentation.http_types.http_response import HttpResponse
from src.shared.config.settings import get_settings

import traceback, sys

_settings = get_settings()

class ExceptionHandler:
    # tuple de TIPOS (classes), sem duplicatas


    @staticmethod
    def handle_exception(e: Exception) -> HttpResponse:
        meta = {}

        if _settings.DEBUG:
            exc_type, exc_value, exc_tb = sys.exc_info()  # informações da exceção
            if exc_tb:
                tb = traceback.extract_tb(sys.exc_info()[2]) # pega a traceback
                if tb:
                    filename, lineno, func, text = tb[-1]         # último frame
                    trace  = f"Erro em {filename}, linha {lineno}, função {func}: {text}"

                    meta["trace"] = trace
                    meta["raw_error"] = str(e)

        if isinstance(e, DomainError):
            http_response = HttpResponse(
                status_code=e.status_code,
                body={
                    "errors": [{
                        "title": e.name,
                        "status": e.status_code,
                        "data": e.message,
                        "details": getattr(e, "details", None),
                    }],
                    "meta": meta,
                },
            )
            return http_response

        return HttpResponse(
            status_code=500,
            body={
                "errors": [{
                    "title": "Internal Server Error",
                    "status": 500,
                }],
                "meta": meta
            }
        )
