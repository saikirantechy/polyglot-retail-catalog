"""Repository protocols and shared helpers."""

from __future__ import annotations

from typing import Any, Protocol

from app.models import Product


def tag_similarity(source: Product, candidate: Product) -> float:
    """Blended Jaccard/category score used when no vector embedding exists."""
    source_tags = {tag.strip().lower() for tag in source.visual_tags if tag.strip()}
    candidate_tags = {tag.strip().lower() for tag in candidate.visual_tags if tag.strip()}
    union = source_tags | candidate_tags
    jaccard = len(source_tags & candidate_tags) / len(union) if union else 0.0
    category_bonus = 0.25 if source.category.lower() == candidate.category.lower() else 0.0
    return round(min(1.0, jaccard * 0.75 + category_bonus), 4)


class CatalogRepository(Protocol):
    name: str

    def list_products(
        self,
        *,
        query: str = "",
        category: str = "",
        max_price: float | None = None,
        in_stock_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        sort: str = "name",
    ) -> list[Product]: ...

    def get_product(self, identifier: str) -> Product | None: ...

    def similar_products(self, identifier: str, limit: int = 5) -> list[Product]: ...

    def categories(self) -> list[str]: ...

    def count(self) -> int: ...


class InteractionRepository(Protocol):
    name: str

    def record_interaction(
        self,
        *,
        user_id: str,
        product_id: str,
        event_type: str,
        score: float,
    ) -> dict[str, Any]: ...

    def interactions_for_product(self, product_id: str, limit: int = 20) -> list[dict[str, Any]]: ...

    def summary(self) -> dict[str, Any]: ...

    def top_products(self, limit: int = 5) -> list[dict[str, Any]]: ...


class AnalyticsRepository(Protocol):
    name: str
    enabled: bool

    def top_products(self, limit: int = 5) -> list[dict[str, Any]]: ...

    def summary(self) -> dict[str, Any]: ...
