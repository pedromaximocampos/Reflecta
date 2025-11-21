from typing import Callable, Optional,  Awaitable, Any
from fastapi import requests as FastAPIRequests
from fastapi.responses import JSONResponse, Response
from src.presentation.http_types import HttpResponse, HttpRequest
from src.presentation.middlewares.exception_handler import ExceptionHandler

ControllerHandle = Callable[[HttpRequest],  Awaitable[HttpResponse]]

async def adapter_fastapi_request( request: FastAPIRequests, controller_handle: ControllerHandle, body_override: Optional[Any] = None) -> Response:
    try:
        if body_override is not None:
            body = body_override
        else:
            try:
                body = await request.json()
            except Exception:
                body = None


        http_request = HttpRequest(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            body=body,
            query_params=dict(request.query_params),
            path_params=request.path_params,
            cookies=request.cookies,
        )


        http_response: HttpResponse = await controller_handle(http_request)
    except Exception as ex:
        http_response = ExceptionHandler.handle_exception(ex)

    response = JSONResponse(
        status_code=http_response.status_code,
        content=http_response.body,
    )

    for name, value in getattr(http_response, "headers", {}).items():
        response.headers[name] = value

    for cookie in getattr(http_response, "cookies", []):
        response.set_cookie(
            key=cookie.name,
            value=cookie.value,
            max_age=cookie.max_age,
            httponly=cookie.httponly,
            secure=cookie.secure,
            samesite=cookie.samesite,
            path=cookie.path,
            domain=cookie.domain,
        )

    return response