from __future__ import annotations

from app.models import Product
from app.repositories.base import tag_similarity


def test_seeding_is_idempotent(services):
    assert services.catalog.count() == 12
    services.startup()
    assert services.catalog.count() == 12
    assert services.analytics.summary()["interaction_rows"] == 32


def test_catalog_filters_are_case_insensitive(services):
    products = services.catalog.list(category="audio")
    assert len(products) == 2
    assert {item["category"] for item in products} == {"Audio"}


def test_similarity_prefers_shared_tags_and_category():
    source = Product(
        product_id="1",
        name="Source",
        sku="SRC-1",
        price=10,
        stock=1,
        category="Audio",
        visual_tags=["wireless", "black"],
    )
    close = Product(
        product_id="2",
        name="Close",
        sku="SRC-2",
        price=10,
        stock=1,
        category="Audio",
        visual_tags=["wireless", "black", "compact"],
    )
    far = Product(
        product_id="3",
        name="Far",
        sku="SRC-3",
        price=10,
        stock=1,
        category="Home",
        visual_tags=["ceramic"],
    )
    assert tag_similarity(source, close) > tag_similarity(source, far)
    assert 0 <= tag_similarity(source, far) <= 1


def test_top_products_have_engagement(services):
    rows = services.analytics.top_products(3)
    assert len(rows) == 3
    scores = [row["score"] for row in rows]
    assert scores == sorted(scores, reverse=True)
    assert all(row["product"] for row in rows)


def test_summary_contains_event_breakdown(services):
    summary = services.analytics.summary()
    assert summary["product_count"] == 12
    assert summary["interaction_rows"] == 32
    assert "purchase" in summary["by_event"]
    assert summary["by_event"]["purchase"] >= 1
