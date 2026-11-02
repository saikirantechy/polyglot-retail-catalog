"""Product catalog API."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.errors import ValidationError
from app.routes import services
from app.routes._utils import bool_arg, int_arg, optional_float_arg

products_bp = Blueprint("products", __name__)
ALLOWED_SORTS = {"name", "price_asc", "price_desc", "stock"}


@products_bp.get("/products")
def list_products():
    query = request.args.get("q", "").strip()[:200]
    category = request.args.get("category", "").strip()[:80]
    sort = request.args.get("sort", "name").strip()
    if sort not in ALLOWED_SORTS:
        raise ValidationError(f"sort must be one of: {', '.join(sorted(ALLOWED_SORTS))}")

    limit = int_arg("limit", 24, 1, 100)
    offset = int_arg("offset", 0, 0, 10_000)
    max_price = optional_float_arg("max_price")

    catalog = services().catalog
    items = catalog.list(
        query=query,
        category=category,
        max_price=max_price,
        in_stock_only=bool_arg("in_stock"),
        limit=limit,
        offset=offset,
        sort=sort,
    )
    return jsonify(
        {
            "items": items,
            "count": len(items),
            "limit": limit,
            "offset": offset,
            "total": catalog.count(),
        }
    )


@products_bp.get("/products/<identifier>")
def get_product(identifier: str):
    return jsonify({"product": services().catalog.get(identifier)})


@products_bp.get("/products/<identifier>/similar")
def similar_products(identifier: str):
    limit = int_arg("limit", 4, 1, 20)
    items = services().catalog.similar(identifier, limit=limit)
    return jsonify({"items": items, "count": len(items)})


@products_bp.get("/categories")
def list_categories():
    items = services().catalog.categories()
    return jsonify({"items": items, "count": len(items)})
