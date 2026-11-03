from src.modules.journal.presentation.share_routes import share_router
from src.modules.operations.presentation.routes import operations_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.modules.auth.presentation.routes import auth_router
from src.modules.catalog.presentation.routes import catalog_router
from src.modules.journal.presentation.routes import journal_router
from src.modules.ai_processing.presentation.routes import ai_processing_router
from src.shared.config.constants import API_VERSION
from src.shared.config.settings import get_settings
from src.main.server.fast_api.fast_api_exception_handler import add_exception_handlers

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
    )

    @app.middleware("http")
    async def protect_shared_responses(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/shared/") or (request.url.path.startswith("/journal/context-analyses/") and "/shares" in request.url.path):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response

    add_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(catalog_router)
    app.include_router(journal_router)
    app.include_router(share_router)
    app.include_router(operations_router)
    app.include_router(ai_processing_router)

    return app
