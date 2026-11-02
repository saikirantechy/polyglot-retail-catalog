"""Agent tools shared by the ADK agent and the in-app Gemini assistant.

Every function returns JSON-serialisable data and never raises at the agent
boundary: failures are reported as ``{"error": ...}`` so the model can explain
the problem instead of crashing.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

LOGGER = logging.getLogger(__name__)

_standalone: Any = None
_trace: ContextVar[dict[str, Any] | None] = ContextVar("assistant_trace", default=None)


@contextmanager
def assistant_trace() -> Iterator[dict[str, Any]]:
    """Collect products and tool calls produced during one assistant turn."""
    trace: dict[str, Any] = {"products": [], "calls": []}
    token = _trace.set(trace)
    try:
        yield trace
    finally:
        _trace.reset(token)


def _record_call(name: str, **arguments: Any) -> None:
    trace = _trace.get()
    if trace is None:
        return
    rendered = ", ".join(f"{key}={value!r}" for key, value in arguments.items())
    trace["calls"].append(f"{name}({rendered})")


def _collect_products(products: list[dict[str, Any]] | None) -> None:
    trace = _trace.get()
    if trace is None or not products:
        return
    seen = {item["product_id"] for item in trace["products"]}
    for product in products:
        if product["product_id"] not in seen:
            trace["products"].append(product)
            seen.add(product["product_id"])


def _services() -> Any:
    global _standalone
    try:
        from flask import current_app, has_app_context

        if has_app_context() and "services" in current_app.extensions:
            return current_app.extensions["services"]
    except Exception:  # pragma: no cover - Flask always present in the app
        pass

    if _standalone is None:
        from app.config import Settings
        from app.services.factory import build_services

        _standalone = build_services(Settings.from_env())
        _standalone.startup()
    return _standalone


def search_products(
    query: str = "",
    category: str = "",
    max_price: float = 0.0,
    in_stock_only: bool = False,
    limit: int = 5,
) -> dict[str, Any]:
    """Search the product catalog.

    Args:
        query: Free-text search across names, descriptions, SKUs and tags.
        category: Optional category such as Audio, Wearables, Home, Photography, Gaming or Accessories.
        max_price: Maximum price in USD. Use 0 for no limit.
        in_stock_only: When true, only return products with stock greater than zero.
        limit: Maximum number of products to return (1-20).

    Returns:
        A dictionary with a 'products' list and a 'count'.
    """
    try:
        cap = max(1, min(int(limit), 20))
        price = float(max_price) if max_price else None
        products = _services().catalog.list(
            query=query,
            category=category,
            max_price=price,
            in_stock_only=bool(in_stock_only),
            limit=cap,
        )
        _record_call(
            "search_products",
            query=query,
            category=category,
            max_price=max_price,
            in_stock_only=in_stock_only,
        )
        _collect_products(products)
        return {"products": products, "count": len(products)}
    except Exception as exc:
        LOGGER.warning("search_products failed", exc_info=True)
        return {"products": [], "count": 0, "error": str(exc)}


def get_product(product_id: str) -> dict[str, Any]:
    """Fetch one product by product ID or SKU.

    Args:
        product_id: The product UUID or the SKU, for example AUD-1001.

    Returns:
        A dictionary with either a 'product' object or an 'error'.
    """
    try:
        product = _services().catalog.get(product_id, required=False)
        _record_call("get_product", product_id=product_id)
        if product is None:
            return {"product": None, "error": f"Product {product_id!r} was not found"}
        _collect_products([product])
        return {"product": product}
    except Exception as exc:
        LOGGER.warning("get_product failed", exc_info=True)
        return {"product": None, "error": str(exc)}


def find_similar_products(product_id: str, limit: int = 5) -> dict[str, Any]:
    """Find products that look or behave like a reference product.

    The cloud implementation uses pgvector image embeddings in AlloyDB. The
    demo implementation blends shared visual tags with category overlap.

    Args:
        product_id: The reference product UUID or SKU.
        limit: Maximum number of similar products to return (1-20).

    Returns:
        A dictionary with a 'products' list and a 'count'.
    """
    try:
        services = _services()
        source = services.catalog.get(product_id, required=False)
        _record_call("find_similar_products", product_id=product_id, limit=limit)
        if source is None:
            return {
                "products": [],
                "count": 0,
                "error": f"Product {product_id!r} was not found",
            }
        products = services.catalog.similar(source["product_id"], limit=limit)
        _collect_products(products)
        return {"products": products, "count": len(products), "reference": source["name"]}
    except Exception as exc:
        LOGGER.warning("find_similar_products failed", exc_info=True)
        return {"products": [], "count": 0, "error": str(exc)}


def check_stock(product_id: str) -> dict[str, Any]:
    """Check live stock for one product.

    Args:
        product_id: The product UUID or SKU.

    Returns:
        Stock details, or an 'error' when the product is unknown.
    """
    try:
        product = _services().catalog.get(product_id, required=False)
        _record_call("check_stock", product_id=product_id)
        if product is None:
            return {"error": f"Product {product_id!r} was not found"}
        return {
            "product_id": product["product_id"],
            "name": product["name"],
            "sku": product["sku"],
            "stock": product["stock"],
            "in_stock": product["in_stock"],
        }
    except Exception as exc:
        LOGGER.warning("check_stock failed", exc_info=True)
        return {"error": str(exc)}


def top_products(limit: int = 5) -> dict[str, Any]:
    """Return the most engaged products from analytics data.

    Args:
        limit: Maximum number of products to return (1-20).

    Returns:
        A dictionary with a 'products' list of analytics rows.
    """
    try:
        rows = _services().analytics.top_products(limit)
        _record_call("top_products", limit=limit)
        _collect_products([row["product"] for row in rows if row.get("product")])
        return {"products": rows, "count": len(rows)}
    except Exception as exc:
        LOGGER.warning("top_products failed", exc_info=True)
        return {"products": [], "count": 0, "error": str(exc)}


def record_interest(
    product_id: str,
    event_type: str = "view",
    user_id: str = "assistant",
) -> dict[str, Any]:
    """Record a customer interaction such as a view, like or cart add.

    Args:
        product_id: The product UUID or SKU.
        event_type: One of view, click, like, add_to_cart or purchase.
        user_id: Identifier for the customer. Defaults to 'assistant'.

    Returns:
        The stored interaction, or an 'error'.
    """
    try:
        interaction = _services().interactions.record(
            user_id=user_id,
            product_id=product_id,
            event_type=event_type,
        )
        _record_call("record_interest", product_id=product_id, event_type=event_type)
        return {"interaction": interaction}
    except Exception as exc:
        LOGGER.warning("record_interest failed", exc_info=True)
        return {"error": str(exc)}


TOOL_FUNCTIONS = [
    search_products,
    get_product,
    find_similar_products,
    check_stock,
    top_products,
    record_interest,
]
