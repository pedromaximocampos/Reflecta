import logging
from time import perf_counter

from src.modules.sharing.presentation import share_router
from src.modules.recommendation.presentation import recommendation_router
from src.modules.operations.presentation.routes import operations_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.modules.auth.presentation.routes import auth_router
from src.modules.catalog.presentation.routes import catalog_router
from src.modules.journal.presentation.routes import journal_router
from src.modules.ai_processing.presentation.routes import ai_processing_router
from src.modules.data_export.presentation import data_export_router
from src.shared.config.constants import API_VERSION
from src.shared.config.settings import get_settings
from src.main.server.fast_api.fast_api_exception_handler import add_exception_handlers

logger = logging.getLogger(__name__)

def create_fast_api_app() -> FastAPI:
    app = FastAPI(
        title="Individuum MVP FastAPI Server",
        description="Backend server for Individuum MVP using FastAPI",
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[get_settings().FRONT_END_DOMAIN.rstrip("/")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition", "Server-Timing", "X-Response-Time-Ms"],
    )

    @app.middleware("http")
    async def report_request_duration(request, call_next):
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (perf_counter() - started_at) * 1000
            route = getattr(request.scope.get("route"), "path", request.url.path)
            logger.warning(
                "Request failed: method=%s route=%s duration_ms=%.1f",
                request.method,
                route,
                elapsed_ms,
            )
            raise

        elapsed_ms = (perf_counter() - started_at) * 1000
        route = getattr(request.scope.get("route"), "path", request.url.path)
        response.headers["Server-Timing"] = f"app;dur={elapsed_ms:.1f}"
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"
        if elapsed_ms >= 750:
            logger.warning(
                "Slow request: method=%s route=%s status=%s duration_ms=%.1f",
                request.method,
                route,
                response.status_code,
                elapsed_ms,
            )
        else:
            logger.debug(
                "Request completed: method=%s route=%s status=%s duration_ms=%.1f",
                request.method,
                route,
                response.status_code,
                elapsed_ms,
            )
        return response

    @app.middleware("http")
    async def protect_shared_responses(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/shared/") or (request.url.path.startswith("/journal/context-analyses/") and "/shares" in request.url.path):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    add_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(catalog_router)
    app.include_router(journal_router)
    app.include_router(share_router)
    app.include_router(recommendation_router)
    app.include_router(operations_router)
    app.include_router(ai_processing_router)
    app.include_router(data_export_router)

    return app
