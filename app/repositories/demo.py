"""SQLite-backed demo repository.

Mirrors the AlloyDB product table plus the MongoDB interaction collection so
the whole application can run locally without any cloud credentials.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.models import Product
from app.repositories.base import tag_similarity

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    category TEXT NOT NULL DEFAULT 'Uncategorised',
    description TEXT NOT NULL DEFAULT '',
    image_url TEXT NOT NULL DEFAULT '',
    visual_tags TEXT NOT NULL DEFAULT '[]',
    attributes TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    score REAL NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_interactions_product
    ON interactions (product_id);
CREATE INDEX IF NOT EXISTS idx_products_category
    ON products (category);
"""


class DemoRepository:
    name = "sqlite-demo"
    enabled = True

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialise(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)
            existing = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            if existing:
                return
            self._seed(connection)

    def _seed(self, connection: sqlite3.Connection) -> None:
        products = json.loads((DATA_DIR / "seed_products.json").read_text(encoding="utf-8"))
        for product in products:
            connection.execute(
                """
                INSERT OR IGNORE INTO products
                    (product_id, name, sku, price, stock, category, description,
                     image_url, visual_tags, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["product_id"],
                    product["name"],
                    product["sku"],
                    float(product["price"]),
                    int(product["stock"]),
                    product.get("category", "Uncategorised"),
                    product.get("description", ""),
                    product.get("image_url", ""),
                    json.dumps(product.get("visual_tags", [])),
                    json.dumps(product.get("attributes", {})),
                ),
            )

        events = json.loads((DATA_DIR / "seed_interactions.json").read_text(encoding="utf-8"))
        now = datetime.now(UTC).isoformat()
        for event in events:
            connection.execute(
                """
                INSERT INTO interactions (user_id, product_id, event_type, score, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event["user_id"],
                    event["product_id"],
                    event["event_type"],
                    float(event["score"]),
                    now,
                ),
            )

    @staticmethod
    def _row_to_product(row: sqlite3.Row) -> Product:
        return Product(
            product_id=row["product_id"],
            name=row["name"],
            sku=row["sku"],
            price=float(row["price"]),
            stock=int(row["stock"]),
            category=row["category"],
            description=row["description"],
            image_url=row["image_url"],
            visual_tags=json.loads(row["visual_tags"] or "[]"),
            attributes=json.loads(row["attributes"] or "{}"),
        )

    def list_products(
        self,
        *,
        query: str = "",
        category: str = "",
        max_price: float | None = None,
        in_stock_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        sort: str = "name",
    ) -> list[Product]:
        clauses: list[str] = []
        params: list[Any] = []

        if category:
            clauses.append("LOWER(category) = LOWER(?)")
            params.append(category)
        if query:
            like = f"%{query}%"
            clauses.append(
                "(name LIKE ? OR description LIKE ? OR category LIKE ? OR sku LIKE ? "
                "OR visual_tags LIKE ?)"
            )
            params.extend([like] * 5)
        if max_price is not None:
            clauses.append("price <= ?")
            params.append(float(max_price))
        if in_stock_only:
            clauses.append("stock > 0")

        order_by = {
            "name": "name ASC",
            "price_asc": "price ASC",
            "price_desc": "price DESC",
            "stock": "stock DESC",
        }.get(sort, "name ASC")

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM products {where} ORDER BY {order_by} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [self._row_to_product(row) for row in rows]

    def get_product(self, identifier: str) -> Product | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM products WHERE product_id = ? OR LOWER(sku) = LOWER(?)",
                (identifier, identifier),
            ).fetchone()
        return self._row_to_product(row) if row else None

    def similar_products(self, identifier: str, limit: int = 5) -> list[Product]:
        source = self.get_product(identifier)
        if source is None:
            return []
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM products WHERE product_id <> ?",
                (source.product_id,),
            ).fetchall()
        scored: list[Product] = []
        for row in rows:
            candidate = self._row_to_product(row)
            candidate.similarity = tag_similarity(source, candidate)
            if candidate.similarity > 0:
                scored.append(candidate)
        scored.sort(key=lambda item: (item.similarity or 0.0, item.name), reverse=True)
        return scored[:limit]

    def categories(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT category FROM products ORDER BY category"
            ).fetchall()
        return [row["category"] for row in rows]

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM products").fetchone()[0])

    def record_interaction(
        self,
        *,
        user_id: str,
        product_id: str,
        event_type: str,
        score: float,
    ) -> dict[str, Any]:
        created_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO interactions (user_id, product_id, event_type, score, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, product_id, event_type, float(score), created_at),
            )
        return {
            "user_id": user_id,
            "product_id": product_id,
            "event_type": event_type,
            "score": round(float(score), 2),
            "created_at": created_at,
        }

    def interactions_for_product(self, product_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT user_id, product_id, event_type, score, created_at
                FROM interactions
                WHERE product_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (product_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def summary(self) -> dict[str, Any]:
        with self._connect() as connection:
            total = connection.execute(
                "SELECT COUNT(*) AS rows, COALESCE(SUM(score), 0) AS score FROM interactions"
            ).fetchone()
            by_event = connection.execute(
                "SELECT event_type, COUNT(*) AS count FROM interactions GROUP BY event_type"
            ).fetchall()
        return {
            "interaction_rows": int(total["rows"]),
            "total_score": round(float(total["score"]), 2),
            "by_event": {row["event_type"]: int(row["count"]) for row in by_event},
        }

    def top_products(self, limit: int = 5) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT product_id,
                       ROUND(SUM(score), 2) AS score,
                       COUNT(*) AS events
                FROM interactions
                GROUP BY product_id
                ORDER BY score DESC, events DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "product_id": row["product_id"],
                "score": float(row["score"]),
                "events": int(row["events"]),
            }
            for row in rows
        ]
