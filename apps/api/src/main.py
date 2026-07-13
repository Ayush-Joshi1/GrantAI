"""
FastAPI app composition entrypoint.

Clean Architecture guideline:
- Routes/controllers: src/api/*
- Use-cases (services): src/application/*
- Domain rules: src/domain/*
- External adapters: src/infrastructure/*
"""

from __future__ import annotations

from fastapi import FastAPI

from src.api.middleware.correlation_id import CorrelationIdMiddleware
from src.api.v1.router import api_v1_router
from src.core.config.settings import Settings, get_settings
from src.core.errors.handlers import register_exception_handlers
from src.core.logging.setup import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    configure_logging(settings)

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        debug=settings.debug,
        description=settings.api_description,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
    )

    app.add_middleware(CorrelationIdMiddleware, header_name=settings.correlation_id_header)

    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    return app


app = create_app()

