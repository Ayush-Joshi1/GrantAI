from __future__ import annotations


class AppError(Exception):
    code = "app_error"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AppError):
    code = "not_found"


class ValidationError(AppError):
    code = "validation_error"


class UpstreamError(AppError):
    code = "upstream_error"

