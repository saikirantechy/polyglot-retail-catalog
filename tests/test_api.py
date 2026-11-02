from __future__ import annotations

HEADPHONES = "11111111-1111-4111-8111-111111111101"


def test_health_reports_demo_backends(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "demo"
    assert payload["product_count"] == 12
    assert payload["backends"]["catalog"] == "sqlite-demo"
    assert payload["backends"]["assistant"] == "rule-based"


def test_list_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 12
    assert payload["total"] == 12
    assert payload["items"][0]["sku"]


def test_filter_by_category(client):
    response = client.get("/api/products?category=Audio")
    payload = response.get_json()
    assert payload["count"] == 2
    assert {item["category"] for item in payload["items"]} == {"Audio"}


def test_search_products(client):
    payload = client.get("/api/products?q=headphones").get_json()
    assert payload["count"] == 1
    assert payload["items"][0]["sku"] == "AUD-1001"


def test_max_price_and_sort(client):
    payload = client.get("/api/products?max_price=100&sort=price_desc").get_json()
    assert payload["count"] >= 1
    prices = [item["price"] for item in payload["items"]]
    assert prices == sorted(prices, reverse=True)
    assert all(price <= 100 for price in prices)


def test_get_product_by_sku_and_uuid(client):
    by_sku = client.get("/api/products/AUD-1001").get_json()["product"]
    by_uuid = client.get(f"/api/products/{HEADPHONES}").get_json()["product"]
    assert by_sku["product_id"] == by_uuid["product_id"] == HEADPHONES
    assert by_sku["attributes"]["color"] == "Midnight Black"


def test_unknown_product_returns_404_json(client):
    response = client.get("/api/products/DOES-NOT-EXIST")
    assert response.status_code == 404
    assert response.get_json()["error"]


def test_similar_products_exclude_reference(client):
    response = client.get(f"/api/products/{HEADPHONES}/similar?limit=3")
    assert response.status_code == 200
    payload = response.get_json()
    assert 1 <= payload["count"] <= 3
    assert all(item["product_id"] != HEADPHONES for item in payload["items"])
    similarities = [item["similarity"] for item in payload["items"]]
    assert similarities == sorted(similarities, reverse=True)
    assert all(0 < value <= 1 for value in similarities)


def test_categories(client):
    payload = client.get("/api/categories").get_json()
    assert "Audio" in payload["items"]
    assert "Accessories" in payload["items"]


def test_record_interaction_and_summary(client):
    before = client.get("/api/analytics/summary").get_json()["interaction_rows"]

    response = client.post(
        "/api/interactions",
        json={
            "user_id": "test-user",
            "product_id": "AUD-1001",
            "event_type": "purchase",
        },
    )
    assert response.status_code == 201
    interaction = response.get_json()["interaction"]
    assert interaction["event_type"] == "purchase"
    assert interaction["score"] == 5.0

    after = client.get("/api/analytics/summary").get_json()
    assert after["interaction_rows"] == before + 1
    assert after["product_count"] == 12
    assert after["top_products"]


def test_invalid_interaction_event(client):
    response = client.post(
        "/api/interactions",
        json={"user_id": "test-user", "product_id": "AUD-1001", "event_type": "refund"},
    )
    assert response.status_code == 400
    assert "event_type" in response.get_json()["error"]


def test_interaction_requires_json(client):
    response = client.post("/api/interactions", data="not-json", content_type="text/plain")
    assert response.status_code == 400


def test_interactions_for_product(client):
    payload = client.get("/api/products/AUD-1001/interactions").get_json()
    assert payload["count"] >= 1
    assert all(item["product_id"] == HEADPHONES for item in payload["items"])


def test_storefront_pages_render(client):
    index = client.get("/")
    assert index.status_code == 200
    assert b"Polyglot Store" in index.data
    assert b"Aurora Wireless Headphones" in index.data

    product = client.get("/product/AUD-1001")
    assert product.status_code == 200
    assert b"Midnight Black" in product.data

    chat = client.get("/chat")
    assert chat.status_code == 200
    assert b"Catalog assistant" in chat.data
