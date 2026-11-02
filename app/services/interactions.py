"""Interaction capture and validation."""

from __future__ import annotations

from typing import Any

from app.errors import NotFoundError, ValidationError

EVENT_SCORES = {
    "view": 1.0,
    "click": 2.0,
    "like": 3.0,
    "add_to_cart": 4.0,
    "purchase": 5.0,
}
ALLOWED_EVENTS = set(EVENT_SCORES)


class InteractionService:
    def __init__(self, repository: Any, catalog: Any) -> None:
        self.repository = repository
        self.catalog = catalog

    @property
    def name(self) -> str:
        return self.repository.name

    def record(
        self,
        *,
        user_id: str,
        product_id: str,
        event_type: str = "view",
        score: float | None = None,
    ) -> dict[str, Any]:
        user_id = (user_id or "").strip()
        if not user_id:
            raise ValidationError("user_id is required")
        if len(user_id) > 128:
            raise ValidationError("user_id must be 128 characters or fewer")
        if event_type not in ALLOWED_EVENTS:
            raise ValidationError(
                f"event_type must be one of: {', '.join(sorted(ALLOWED_EVENTS))}"
            )

        product = self.catalog.get(product_id, required=False)
        if product is None:
            raise NotFoundError(f"Product {product_id!r} was not found")

        resolved_score = EVENT_SCORES[event_type] if score is None else float(score)
        if not 0 <= resolved_score <= 100:
            raise ValidationError("score must be between 0 and 100")

        return self.repository.record_interaction(
            user_id=user_id,
            product_id=product["product_id"],
            event_type=event_type,
            score=resolved_score,
        )

    def for_product(self, product_id: str, limit: int = 20) -> list[dict[str, Any]]:
        product = self.catalog.get(product_id, required=False)
        if product is None:
            raise NotFoundError(f"Product {product_id!r} was not found")
        limit = max(1, min(int(limit), 100))
        return self.repository.interactions_for_product(product["product_id"], limit=limit)
