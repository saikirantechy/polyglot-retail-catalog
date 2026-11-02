from __future__ import annotations


def test_chat_search_with_price_filter(client):
    response = client.post(
        "/api/chat",
        json={"message": "wireless headphones under $200", "user_id": "test-user"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "demo"
    assert payload["notice"]
    assert payload["tool_calls"]
    assert payload["products"]
    assert all(product["price"] <= 200 for product in payload["products"])


def test_chat_similar_products(client):
    response = client.post(
        "/api/chat",
        json={"message": "Find products similar to AUD-1001", "user_id": "test-user"},
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["products"]
    assert payload["products"][0]["product_id"] != "11111111-1111-4111-8111-111111111101"
    assert "similar" in payload["reply"].lower()


def test_chat_popular_products(client):
    response = client.post(
        "/api/chat",
        json={"message": "What is popular right now?", "user_id": "test-user"},
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["products"]
    assert any("top_products" in call for call in payload["tool_calls"])


def test_chat_stock_filter(client):
    response = client.post(
        "/api/chat",
        json={"message": "Do you have fitness wearables in stock?", "user_id": "test-user"},
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["products"]
    assert all(product["in_stock"] for product in payload["products"])
    assert all(product["category"] == "Wearables" for product in payload["products"])


def test_chat_help(client):
    response = client.post("/api/chat", json={"message": "hello", "user_id": "test-user"})
    payload = response.get_json()
    assert response.status_code == 200
    assert "search the catalog" in payload["reply"]


def test_chat_rejects_empty_message(client):
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 400


def test_chat_rejects_bad_history(client):
    response = client.post(
        "/api/chat",
        json={"message": "hello", "history": "not-a-list"},
    )
    assert response.status_code == 400
