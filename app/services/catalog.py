"""Catalog use cases."""

from __future__ import annotations

from typing import Any

from app.errors import NotFoundError


class CatalogService:
    def __init__(self, repository: Any) -> None:
        self.repository = repository

    @property
    def name(self) -> str:
        return self.repository.name

    def list(
        self,
        *,
        query: str = "",
        category: str = "",
        max_price: float | None = None,
        in_stock_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        sort: str = "name",
    ) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 100))
        offset = max(0, int(offset))
        products = self.repository.list_products(
            query=query.strip(),
            category=category.strip(),
            max_price=max_price,
            in_stock_only=in_stock_only,
            limit=limit,
            offset=offset,
            sort=sort,
        )
        return [product.to_dict() for product in products]

    def get(self, identifier: str, *, required: bool = True) -> dict[str, Any] | None:
        product = self.repository.get_product(identifier)
        if product is None:
            if required:
                raise NotFoundError(f"Product {identifier!r} was not found")
            return None
        return product.to_dict()

    def similar(self, identifier: str, limit: int = 5) -> list[dict[str, Any]]:
        if self.repository.get_product(identifier) is None:
            raise NotFoundError(f"Product {identifier!r} was not found")
        limit = max(1, min(int(limit), 20))
        products = self.repository.similar_products(identifier, limit=limit)
        return [product.to_dict() for product in products]

    def categories(self) -> list[str]:
        return self.repository.categories()

    def count(self) -> int:
        return self.repository.count()
