from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.presentation.middlewares.exception_handler import ExceptionHandler
from src.domain.exceptions.api_types.validation_error import ValidationFailed
from src.domain.exceptions.domain_error import DomainError


def add_exception_handlers(app: FastAPI) -> None:
    """
    Conecta erros do FastAPI/Pydantic ao seu protocolo de erros de domínio.
    """

    # --------------------------
    # 1) Erros de validação Pydantic (entrada inválida)
    # --------------------------
    @app.exception_handler(RequestValidationError)
    async def pydantic_error_handler(request: Request, exc: RequestValidationError):
        """
        Traduz erro de Pydantic para seu ValidationFailed (DomainError).
        """
        domain_exc = ValidationFailed(
            message="Invalid request data",
            details=exc.errors(),
        )

        http_response = ExceptionHandler.handle_exception(domain_exc)

        return JSONResponse(
            status_code=http_response.status_code,
            content=http_response.body,
        )

    # --------------------------
    # 2) DomainError que escape do adapter (raro)
    # --------------------------
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        """
        Se alguma DomainError escapar do adapter, trata aqui igual ao ExceptionHandler.
        """
        http_response = ExceptionHandler.handle_exception(exc)

        return JSONResponse(
            status_code=http_response.status_code,
            content=http_response.body,
        )

    # --------------------------
    # 3) Erros inesperados de FastAPI (último fallback)
    # --------------------------
    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        """
        Evita leaks de stack trace para o cliente em erros fora do seu fluxo.
        """
        http_response = ExceptionHandler.handle_exception(exc)

        return JSONResponse(
            status_code=http_response.status_code,
            content=http_response.body,
        )
