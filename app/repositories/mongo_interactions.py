"""MongoDB Atlas interaction and flexible-attribute repository."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

LOGGER = logging.getLogger(__name__)

INTERACTIONS = "user_interactions_collection"
PRODUCT_DETAILS = "product_details_collection"


class MongoRepository:
    name = "mongodb-atlas"

    def __init__(self, uri: str, database: str = "ecommerce_db") -> None:
        self.uri = uri
        self.database = database
        self._client: Any = None

    def _db(self) -> Any:
        if self._client is None:
            try:
                from pymongo import MongoClient
            except ImportError as exc:  # pragma: no cover - depends on environment
                raise RuntimeError(
                    "pymongo is required for MongoDB mode. "
                    "Install requirements-cloud.txt or unset MONGODB_URI."
                ) from exc
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
        return self._client[self.database]

    # -- product details -------------------------------------------------
    def get_attributes(self, sku: str, product_id: str) -> dict[str, Any]:
        document = self._db()[PRODUCT_DETAILS].find_one(
            {"$or": [{"sku": sku}, {"product_id": product_id}]},
            {"_id": 0, "attributes": 1, "details": 1},
        )
        if not document:
            return {}
        return dict(document.get("attributes") or document.get("details") or {})

    # -- interactions ----------------------------------------------------
    def record_interaction(
        self,
        *,
        user_id: str,
        product_id: str,
        event_type: str,
        score: float,
    ) -> dict[str, Any]:
        created_at = datetime.now(UTC)
        document = {
            "user_id": user_id,
            "product_id": product_id,
            "event_type": event_type,
            "score": float(score),
            "created_at": created_at,
        }
        self._db()[INTERACTIONS].insert_one(document)
        return {
            "user_id": user_id,
            "product_id": product_id,
            "event_type": event_type,
            "score": round(float(score), 2),
            "created_at": created_at.isoformat(),
        }

    def interactions_for_product(self, product_id: str, limit: int = 20) -> list[dict[str, Any]]:
        cursor = (
            self._db()[INTERACTIONS]
            .find({"product_id": product_id}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [
            {
                "user_id": item.get("user_id"),
                "product_id": item.get("product_id"),
                "event_type": item.get("event_type"),
                "score": round(float(item.get("score", 0)), 2),
                "created_at": item["created_at"].isoformat()
                if isinstance(item.get("created_at"), datetime)
                else item.get("created_at"),
            }
            for item in cursor
        ]

    def summary(self) -> dict[str, Any]:
        collection = self._db()[INTERACTIONS]
        totals = list(
            collection.aggregate(
                [{"$group": {"_id": None, "rows": {"$sum": 1}, "score": {"$sum": "$score"}}}]
            )
        )
        by_event = collection.aggregate(
            [{"$group": {"_id": "$event_type", "count": {"$sum": 1}}}]
        )
        total = totals[0] if totals else {"rows": 0, "score": 0}
        return {
            "interaction_rows": int(total.get("rows", 0)),
            "total_score": round(float(total.get("score", 0)), 2),
            "by_event": {item["_id"]: int(item["count"]) for item in by_event},
        }

    def top_products(self, limit: int = 5) -> list[dict[str, Any]]:
        pipeline = [
            {
                "$group": {
                    "_id": "$product_id",
                    "score": {"$sum": "$score"},
                    "events": {"$sum": 1},
                }
            },
            {"$sort": {"score": -1, "events": -1}},
            {"$limit": limit},
        ]
        return [
            {
                "product_id": item["_id"],
                "score": round(float(item.get("score", 0)), 2),
                "events": int(item.get("events", 0)),
            }
            for item in self._db()[INTERACTIONS].aggregate(pipeline)
        ]
