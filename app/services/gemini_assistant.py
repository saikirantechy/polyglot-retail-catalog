"""Gemini-backed assistant using Vertex AI function calling."""

from __future__ import annotations

import logging
from typing import Any

from app.tools import TOOL_FUNCTIONS, assistant_trace

LOGGER = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are the Polyglot Store assistant, a helpful ecommerce catalog agent.

Rules:
- Always call a tool before mentioning a product, price, stock level or popularity.
- Never invent products, prices, stock, reviews or interaction data.
- Prefer search_products, find_similar_products, check_stock and top_products.
- Use record_interest only when the customer clearly wants to save or track a product.
- Keep replies to 2-4 sentences. The interface renders product cards separately, so
  refer to products by name instead of repeating all of their details.
- If a tool returns an error, explain the problem briefly and suggest a next step.
"""


class GeminiAssistant:
    backend_name = "gemini"

    def __init__(self, settings: Any, catalog: Any, interactions: Any, analytics: Any) -> None:
        self.settings = settings
        self.catalog = catalog
        self.interactions = interactions
        self.analytics = analytics

    @property
    def available(self) -> bool:
        if not self.settings.gemini_enabled:
            return False
        try:
            from google import genai  # noqa: F401
        except Exception:
            return False
        return True

    def reply(
        self,
        message: str,
        *,
        user_id: str = "web-demo",
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        del user_id
        from google import genai
        from google.genai import types

        client = genai.Client(
            vertexai=True,
            project=self.settings.project_id,
            location=self.settings.google_cloud_location,
        )

        contents: list[Any] = []
        for turn in history or []:
            role = "user" if turn["role"] == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part(text=turn["content"])])
            )
        contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

        with assistant_trace() as trace:
            response = client.models.generate_content(
                model=self.settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=TOOL_FUNCTIONS,
                    temperature=0.2,
                ),
            )
            products = list(trace["products"])
            tool_calls = list(trace["calls"])

        text = (getattr(response, "text", None) or "").strip()
        if not text:
            text = (
                "I found matching products in the catalog. Review the cards below."
                if products
                else "I could not produce an answer from the catalog tools."
            )

        return {
            "reply": text,
            "products": products,
            "mode": "gemini",
            "notice": "",
            "tool_calls": tool_calls,
        }
