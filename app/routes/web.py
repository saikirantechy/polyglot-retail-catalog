"""Server-rendered storefront pages."""

from __future__ import annotations

import logging

from flask import Blueprint, render_template, request

from app.routes import services

LOGGER = logging.getLogger(__name__)
web_bp = Blueprint("web", __name__)


def _query_filters() -> tuple[str, str, float | None]:
    query = request.args.get("q", "").strip()[:200]
    category = request.args.get("category", "").strip()[:80]
    raw_price = request.args.get("max_price", "").strip()
    max_price = None
    if raw_price:
        try:
            max_price = max(0.0, float(raw_price))
        except ValueError:
            max_price = None
    return query, category, max_price


@web_bp.get("/")
def index():
    query, category, max_price = _query_filters()
    catalog = services().catalog
    products = catalog.list(
        query=query,
        category=category,
        max_price=max_price,
        limit=24,
        sort=request.args.get("sort", "name"),
    )
    try:
        product_count = catalog.count()
    except Exception:
        LOGGER.warning("Could not count products for landing page", exc_info=True)
        product_count = None
    return render_template(
        "index.html",
        products=products,
        categories=catalog.categories(),
        q=query,
        category=category,
        max_price=max_price,
        product_count=product_count,
    )


@web_bp.get("/product/<identifier>")
def product_detail(identifier: str):
    catalog = services().catalog
    product = catalog.get(identifier)
    similar = catalog.similar(identifier, limit=3)
    return render_template("product.html", product=product, similar=similar)


@web_bp.get("/chat")
def chat_page():
    return render_template(
        "chat.html",
        suggestions=[
            "Wireless headphones under $200",
            "Show me products similar to AUD-1001",
            "What is popular right now?",
            "Do you have fitness wearables in stock?",
        ],
    )
