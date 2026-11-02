"""Domain objects shared by repositories, services and tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Product:
    product_id: str
    name: str
    sku: str
    price: float
    stock: int
    category: str = "Uncategorised"
    description: str = ""
    image_url: str = ""
    visual_tags: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    similarity: float | None = None

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "product_id": self.product_id,
            "name": self.name,
            "sku": self.sku,
            "price": round(float(self.price), 2),
            "stock": int(self.stock),
            "in_stock": self.in_stock,
            "category": self.category,
            "description": self.description,
            "image_url": self.image_url,
            "visual_tags": list(self.visual_tags),
            "attributes": dict(self.attributes),
        }
        if self.similarity is not None:
            data["similarity"] = round(float(self.similarity), 4)
        return data


@dataclass
class Interaction:
    user_id: str
    product_id: str
    event_type: str
    score: float
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "event_type": self.event_type,
            "score": round(float(self.score), 2),
            "created_at": self.created_at,
        }
