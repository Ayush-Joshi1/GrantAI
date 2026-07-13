from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog

from src.core.errors.exceptions import AppError, UpstreamError, ValidationError

log = structlog.get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        request_id = request.headers.get("X-Request-Id")
        log.warning("app_error", code=exc.code, message=exc.message, request_id=request_id)
        status_code = 400
        if isinstance(exc, ValidationError):
            status_code = 422
        elif isinstance(exc, UpstreamError):
            status_code = 502

        return JSONResponse(
            status_code=status_code,
            content={
                "request_id": request_id,
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_error(request: Request, exc: Exception):
        request_id = request.headers.get("X-Request-Id")
        log.exception("unhandled_error", request_id=request_id)
        return JSONResponse(
            status_code=500,
            content={
                "request_id": request_id,
                "error": "internal_error",
                "message": "An unexpected error occurred.",
            },
        )

