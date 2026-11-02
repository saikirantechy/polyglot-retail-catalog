"""Analytics API."""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.routes import services
from app.routes._utils import int_arg

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/analytics/summary")
def analytics_summary():
    return jsonify(services().analytics.summary())


@analytics_bp.get("/analytics/top-products")
def analytics_top_products():
    limit = int_arg("limit", 5, 1, 50)
    items = services().analytics.top_products(limit)
    return jsonify({"items": items, "count": len(items)})
