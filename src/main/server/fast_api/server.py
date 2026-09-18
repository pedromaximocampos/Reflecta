from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.modules.auth.presentation.routes import auth_router
from src.modules.catalog.presentation.routes import catalog_router
from src.modules.journal.presentation.routes import journal_router
from src.shared.config.constants import API_VERSION
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
        allow_origins=["*"],  # em produção, restringir
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(catalog_router)
    app.include_router(journal_router)

    return app
