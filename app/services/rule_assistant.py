"""Deterministic assistant used in demo mode and as a cloud fallback."""

from __future__ import annotations

import re
from typing import Any

PRICE_PATTERNS = [
    r"(?:under|below|less than|cheaper than|up to|max(?:imum)?(?: price)?(?: of)?)\s*\$?\s*(\d+(?:\.\d+)?)",
    r"\$\s*(\d+(?:\.\d+)?)",
]
SIMILAR_PATTERN = re.compile(
    r"(?:similar to|alternatives? to|like)\s+(.+?)(?:\s+(?:under|below|less than|in stock|available)\b|$)",
    re.IGNORECASE,
)
CATEGORY_HINTS = {
    "audio": {"audio", "headphone", "headphones", "earbud", "earbuds", "speaker", "sound"},
    "wearables": {"wearable", "wearables", "watch", "smartwatch", "fitness", "band", "tracker"},
    "home": {"home", "lamp", "planter", "decor", "desk", "furniture"},
    "photography": {"camera", "cameras", "photography", "lens", "mirrorless", "action"},
    "gaming": {"gaming", "keyboard", "mouse", "gamer"},
    "accessories": {"accessory", "accessories", "backpack", "sleeve", "bag"},
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "any",
    "are",
    "available",
    "below",
    "best",
    "buy",
    "can",
    "cheaper",
    "dollars",
    "find",
    "for",
    "get",
    "good",
    "i",
    "in",
    "is",
    "less",
    "like",
    "look",
    "looking",
    "max",
    "me",
    "need",
    "of",
    "please",
    "price",
    "product",
    "products",
    "show",
    "similar",
    "some",
    "stock",
    "than",
    "that",
    "the",
    "to",
    "under",
    "usd",
    "want",
    "with",
}
POPULAR_HINTS = {"popular", "trending", "top products", "top sellers", "best seller", "most popular"}
GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon"}
CATEGORY_WORDS = set().union(*CATEGORY_HINTS.values())


class RuleBasedAssistant:
    backend_name = "rule-based"

    def __init__(self, catalog: Any, interactions: Any, analytics: Any) -> None:
        self.catalog = catalog
        self.interactions = interactions
        self.analytics = analytics

    def reply(
        self,
        message: str,
        *,
        user_id: str = "web-demo",
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        del user_id, history  # deterministic mode intentionally ignores conversation state
        text = message.strip()
        lowered = text.lower()
        calls: list[str] = []

        if self._is_help(lowered):
            return self._response(self._help_text(), [], calls)

        max_price = self._price(lowered)
        category = self._category(lowered)
        in_stock_only = any(
            phrase in lowered for phrase in ("in stock", "available", "instock")
        )

        similar_target = self._similar_target(text)
        if similar_target:
            source = self._find_product(similar_target)
            if source:
                calls.append(f"find_similar_products({source['product_id']!r})")
                products = self.catalog.similar(source["product_id"], limit=4)
                if products:
                    return self._response(
                        f"Products similar to {source['name']} based on shared visual tags and category:",
                        products,
                        calls,
                    )
                return self._response(
                    f"I could not find enough tag overlap around {source['name']} to suggest alternatives.",
                    [],
                    calls,
                )

        if any(hint in lowered for hint in POPULAR_HINTS):
            calls.append("top_products(limit=5)")
            rows = self.analytics.top_products(5)
            products = [row["product"] for row in rows if row.get("product")]
            if products:
                return self._response(
                    "The products with the most interaction weight in analytics are:",
                    products,
                    calls,
                )

        query = self._query(lowered)
        calls.append(
            "search_products("
            f"query={query!r}, category={category!r}, max_price={max_price!r}, "
            f"in_stock_only={in_stock_only!r})"
        )
        products = self.catalog.list(
            query=query,
            category=category,
            max_price=max_price,
            in_stock_only=in_stock_only,
            limit=5,
        )

        if not products and query:
            products = self.catalog.list(
                query="",
                category=category,
                max_price=max_price,
                in_stock_only=in_stock_only,
                limit=5,
            )

        if not products:
            return self._response(
                "I could not find a matching product. Try a category such as Audio, "
                "Wearables or Home, ask for something 'under $150', or say "
                "'show me products similar to AUD-1001'.",
                [],
                calls,
            )

        qualifier = "in stock " if in_stock_only else ""
        category_text = f" in {category}" if category else ""
        price_text = f" under ${max_price:.2f}" if max_price else ""
        names = ", ".join(product["name"] for product in products[:3])
        return self._response(
            f"I found {len(products)} {qualifier}product(s){category_text}{price_text}. "
            f"Top matches: {names}.",
            products,
            calls,
        )

    # -- parsing helpers -------------------------------------------------
    @staticmethod
    def _is_help(lowered: str) -> bool:
        return (
            lowered in GREETINGS
            or "help" in lowered
            or "what can you do" in lowered
            or not lowered.strip()
        )

    @staticmethod
    def _help_text() -> str:
        return (
            "I can search the catalog, filter by category or price, find visually "
            "similar products, check stock and show popular items. Try: "
            "'wireless headphones under $200', 'show me products similar to AUD-1001', "
            "or 'what is popular right now?'"
        )

    @staticmethod
    def _price(lowered: str) -> float | None:
        for pattern in PRICE_PATTERNS:
            match = re.search(pattern, lowered)
            if match:
                return float(match.group(1))
        return None

    @staticmethod
    def _category(lowered: str) -> str:
        for category, hints in CATEGORY_HINTS.items():
            if any(re.search(rf"\b{re.escape(hint)}\b", lowered) for hint in hints):
                return category.capitalize()
        return ""

    @staticmethod
    def _similar_target(text: str) -> str:
        match = SIMILAR_PATTERN.search(text)
        if not match:
            return ""
        return match.group(1).strip(" .?!")[:80]

    @staticmethod
    def _query(lowered: str) -> str:
        cleaned = SIMILAR_PATTERN.sub(" ", lowered)
        for pattern in PRICE_PATTERNS:
            cleaned = re.sub(pattern, " ", cleaned)
        words = re.findall(r"[a-z0-9][a-z0-9-]*", cleaned)
        return " ".join(
            word
            for word in words
            if word not in STOPWORDS and word not in CATEGORY_WORDS and not word.isdigit()
        )

    def _find_product(self, target: str) -> dict[str, Any] | None:
        candidates = self.catalog.list(query=target, limit=1)
        if candidates:
            return candidates[0]
        for product in self.catalog.list(limit=100):
            if target.lower() in product["name"].lower():
                return product
        return None

    def _response(
        self,
        reply: str,
        products: list[dict[str, Any]],
        calls: list[str],
    ) -> dict[str, Any]:
        return {
            "reply": reply,
            "products": products,
            "mode": "demo" if self.interactions.name == "sqlite-demo" else "local",
            "notice": (
                "Demo mode: answers use the seeded catalog and tag-based similarity. "
                "Configure a Google Cloud project to enable Gemini and pgvector search."
            ),
            "tool_calls": calls,
        }
