# src/presentation/exception_handler.py
from typing import Tuple, Type

from src.presentation.http_types.http_response import HttpResponse
from src.core.settings import get_settings

import traceback, sys
from src.domain.exceptions.api_types import *

_settings = get_settings()

class ExceptionHandler:
    # tuple de TIPOS (classes), sem duplicatas
    API_EXCEPTIONS: Tuple[Type[Exception], ...] = (
        BadRequestError,
        AuthError,
        UserIsNotAdmin,
        CacheError,
        ConflictError,
        UpgradeRequired,
        DatabaseError,
        NotFoundError,
        ValidationFailed,
        ForbiddenError,
    )

    @staticmethod
    def handle_exception(e: Exception) -> HttpResponse:
        meta = {}

        if _settings.debug:
            exc_type, exc_value, exc_tb = sys.exc_info()  # informações da exceção
            if exc_tb:
                tb = traceback.extract_tb(sys.exc_info()[2]) # pega a traceback
                if tb:
                    filename, lineno, func, text = tb[-1]         # último frame
                    trace  = f"Erro em {filename}, linha {lineno}, função {func}: {text}"

                    meta =  trace

        if isinstance(e, ExceptionHandler.API_EXCEPTIONS):
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