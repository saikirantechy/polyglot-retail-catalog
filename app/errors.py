"""Small exception hierarchy used by the API layer."""

from __future__ import annotations

from typing import Any


class ApiError(Exception):
    def __init__(
        self,
        message: str,
        status: int = 400,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.details = details or {}


class NotFoundError(ApiError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, 404)


class ValidationError(ApiError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, 400, details=details)
