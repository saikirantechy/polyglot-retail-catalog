"""Health and capability endpoint."""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify

from app.routes import services

LOGGER = logging.getLogger(__name__)
health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    service_container = services()
    status = "ok"
    product_count = None
    try:
        product_count = service_container.catalog.count()
    except Exception:
        status = "degraded"
        LOGGER.exception("Catalog health check failed")

    return jsonify(
        {
            "status": status,
            "mode": service_container.mode,
            "backends": service_container.backends(),
            "product_count": product_count,
            "mcp_toolbox_configured": bool(service_container.settings.mcp_toolbox_url),
        }
    )
