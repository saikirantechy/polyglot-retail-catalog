"""Interaction capture API."""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.errors import ValidationError
from app.routes import services
from app.routes._utils import int_arg, json_body, text_field

interactions_bp = Blueprint("interactions", __name__)


@interactions_bp.post("/interactions")
def create_interaction():
    payload = json_body()
    user_id = text_field(payload, "user_id", default="web-demo", max_length=128)
    product_id = text_field(payload, "product_id", max_length=128)
    event_type = text_field(payload, "event_type", default="view", max_length=32)

    score = payload.get("score")
    if score is not None:
        try:
            score = float(score)
        except (TypeError, ValueError) as exc:
            raise ValidationError("score must be a number") from exc

    interaction = services().interactions.record(
        user_id=user_id,
        product_id=product_id,
        event_type=event_type,
        score=score,
    )
    return jsonify({"interaction": interaction}), 201


@interactions_bp.get("/products/<identifier>/interactions")
def product_interactions(identifier: str):
    limit = int_arg("limit", 20, 1, 100)
    items = services().interactions.for_product(identifier, limit=limit)
    return jsonify({"items": items, "count": len(items)})
