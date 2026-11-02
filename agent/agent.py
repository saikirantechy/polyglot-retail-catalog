"""Google ADK agent definition.

Run locally:

    pip install -r requirements-agent.txt
    adk web

Then select the ``agent`` folder. The same root agent can be wrapped for
Vertex AI Agent Engine deployment.
"""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent

from app.tools import (
    check_stock,
    find_similar_products,
    get_product,
    record_interest,
    search_products,
    top_products,
)

INSTRUCTION = """You are the Polyglot Store catalog agent for a multi-database retail demo.

Your job is to help customers discover products using the available tools:
- search_products: free-text, category, price and stock filters.
- get_product: exact product lookup by UUID or SKU.
- find_similar_products: visual/tag similarity. AlloyDB uses pgvector image
  embeddings in cloud mode; demo mode blends visual tags and category overlap.
- check_stock: live stock before claiming availability.
- top_products: engagement analytics from BigQuery or the demo interaction store.
- record_interest: save a view, like, cart add or purchase event when the
  customer clearly asks to track something.

Rules:
1. Always call a tool before stating a price, stock level or recommendation.
2. Never invent products, reviews or interaction data.
3. Explain the evidence briefly: name the constraint or similarity signal used.
4. Keep answers short and refer to products by name.
5. If a tool returns an error, explain it and suggest a next step.
"""

root_agent = LlmAgent(
    name="polyglot_retail_catalog_agent",
    model=os.getenv("MODEL", os.getenv("GEMINI_MODEL", "gemini-2.5-flash")),
    description=(
        "Catalog assistant that searches AlloyDB, MongoDB and BigQuery through "
        "shared tools for product discovery, stock and analytics."
    ),
    instruction=INSTRUCTION,
    tools=[
        search_products,
        get_product,
        find_similar_products,
        check_stock,
        top_products,
        record_interest,
    ],
)
