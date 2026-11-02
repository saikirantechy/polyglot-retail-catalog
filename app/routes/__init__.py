"""HTTP route blueprints."""

from __future__ import annotations

from typing import Any

from flask import current_app


def services() -> Any:
    return current_app.extensions["services"]
