"""Analytics use cases with graceful fallbacks between BigQuery and Mongo."""

from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, analytics: Any, interactions: Any, catalog: Any) -> None:
        self.analytics = analytics
        self.interactions = interactions
        self.catalog = catalog

    @property
    def name(self) -> str:
        return self.analytics.name

    def _rows(self, limit: int) -> list[dict[str, Any]]:
        try:
            return self.analytics.top_products(limit)
        except Exception:
            LOGGER.warning("Analytics backend failed, trying interaction store", exc_info=True)
        try:
            return self.interactions.top_products(limit)
        except Exception:
            LOGGER.warning("Interaction store analytics failed", exc_info=True)
            return []

    def top_products(self, limit: int = 5) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 50))
        results: list[dict[str, Any]] = []
        for row in self._rows(limit):
            product = self.catalog.get(row["product_id"], required=False)
            results.append(
                {
                    "product_id": row["product_id"],
                    "name": product["name"] if product else row["product_id"],
                    "sku": product["sku"] if product else "",
                    "price": product["price"] if product else None,
                    "score": row.get("score", 0),
                    "events": row.get("events", 0),
                    "product": product,
                }
            )
        return results

    def summary(self) -> dict[str, Any]:
        try:
            base = self.analytics.summary()
        except Exception:
            LOGGER.warning("Analytics summary failed, trying interaction store", exc_info=True)
            try:
                base = self.interactions.summary()
            except Exception:
                LOGGER.warning("Interaction summary failed", exc_info=True)
                base = {"interaction_rows": 0, "total_score": 0, "by_event": {}}

        try:
            product_count = self.catalog.count()
        except Exception:
            LOGGER.warning("Could not count catalog products", exc_info=True)
            product_count = None

        return {
            "product_count": product_count,
            "interaction_rows": base.get("interaction_rows", 0),
            "total_score": base.get("total_score", 0),
            "by_event": base.get("by_event", {}),
            "top_products": self.top_products(5),
        }
