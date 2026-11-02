"""Request parsing helpers shared by API blueprints."""

from __future__ import annotations

from typing import Any

from flask import request

from app.errors import ValidationError

TRUTHY = {"1", "true", "yes", "on"}


def int_arg(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise ValidationError(f"{name} must be between {minimum} and {maximum}")
    return value


def optional_float_arg(name: str, minimum: float = 0.0, maximum: float = 1_000_000.0) -> float | None:
    raw = request.args.get(name)
    if raw is None or raw.strip() == "":
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} must be a number") from exc
    if not minimum <= value <= maximum:
        raise ValidationError(f"{name} must be between {minimum} and {maximum}")
    return value


def bool_arg(name: str, default: bool = False) -> bool:
    raw = request.args.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in TRUTHY


def json_body() -> dict[str, Any]:
    if not request.is_json:
        raise ValidationError("Content-Type must be application/json")
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")
    return payload


def text_field(
    payload: dict[str, Any],
    name: str,
    *,
    required: bool = True,
    default: str = "",
    max_length: int = 255,
) -> str:
    value = payload.get(name, default)
    if value is None:
        value = default
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string")
    value = value.strip()
    if required and not value:
        raise ValidationError(f"{name} is required")
    if len(value) > max_length:
        raise ValidationError(f"{name} must be {max_length} characters or fewer")
    return value
