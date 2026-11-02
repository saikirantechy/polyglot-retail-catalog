"""AlloyDB for PostgreSQL catalog repository.

The codelab schema (``alloydb/01_schema.sql``) only contains the five core
columns. ``alloydb/04_app_extension.sql`` adds the optional storefront columns
and the pgvector embedding. This repository detects which columns exist so it
still works against the original schema.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from app.models import Product
from app.repositories.base import tag_similarity

LOGGER = logging.getLogger(__name__)

TABLE = "products_core_table"
OPTIONAL_COLUMNS = {"category", "description", "image_url", "visual_tags", "img_embeddings"}
SORT_ORDERS = {
    "name": "name ASC",
    "price_asc": "price ASC",
    "price_desc": "price DESC",
    "stock": "stock DESC",
}


class PostgresCatalogRepository:
    name = "alloydb"

    def __init__(self, dsn: str, attributes_provider: Any | None = None) -> None:
        self.dsn = dsn
        self.attributes_provider = attributes_provider
        self._columns: set[str] | None = None
        self._pool: Any = None

    # -- connections -----------------------------------------------------
    def _get_pool(self) -> Any:
        if self._pool is False:
            return None
        if self._pool is None:
            try:
                from psycopg.rows import dict_row
                from psycopg_pool import ConnectionPool

                self._pool = ConnectionPool(
                    self.dsn,
                    min_size=0,
                    max_size=5,
                    timeout=10,
                    open=True,
                    kwargs={"row_factory": dict_row},
                )
            except Exception:  # pragma: no cover - depends on installed extras
                LOGGER.debug("psycopg pool unavailable, using per-call connections", exc_info=True)
                self._pool = False
        return self._pool or None

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise RuntimeError(
                "psycopg is required for AlloyDB mode. "
                "Install requirements-cloud.txt or unset ALLOYDB_DSN."
            ) from exc

        pool = self._get_pool()
        if pool is not None:
            with pool.connection() as connection:
                yield connection
            return
        with psycopg.connect(self.dsn, connect_timeout=10, row_factory=dict_row) as connection:
            yield connection

    # -- schema introspection -------------------------------------------
    def _table_columns(self, connection: Any) -> set[str]:
        if self._columns is None:
            rows = connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = current_schema() AND table_name = %s
                """,
                (TABLE,),
            ).fetchall()
            columns = {row["column_name"] for row in rows}
            if not columns:
                raise RuntimeError(
                    f"Table {TABLE} was not found. Run alloydb/01_schema.sql in AlloyDB Studio first."
                )
            self._columns = columns
        return self._columns

    @staticmethod
    def _select_list(columns: set[str]) -> str:
        parts = ["product_id", "name", "sku", "price", "stock"]
        parts.append("category" if "category" in columns else "NULL::text AS category")
        parts.append("description" if "description" in columns else "''::text AS description")
        parts.append("image_url" if "image_url" in columns else "''::text AS image_url")
        parts.append(
            "visual_tags" if "visual_tags" in columns else "ARRAY[]::text[] AS visual_tags"
        )
        return ", ".join(parts)

    def _row_to_product(self, row: dict[str, Any], similarity: float | None = None) -> Product:
        attributes: dict[str, Any] = {}
        if self.attributes_provider is not None:
            try:
                attributes = self.attributes_provider.get_attributes(row["sku"], row["product_id"])
            except Exception:  # pragma: no cover - Mongo optional
                LOGGER.warning("Could not load Mongo attributes for sku=%s", row["sku"], exc_info=True)
        return Product(
            product_id=str(row["product_id"]),
            name=row["name"],
            sku=row["sku"],
            price=float(row["price"]),
            stock=int(row["stock"]),
            category=row.get("category") or "Uncategorised",
            description=row.get("description") or "",
            image_url=row.get("image_url") or "",
            visual_tags=list(row.get("visual_tags") or []),
            attributes=attributes,
            similarity=similarity,
        )

    # -- catalog ---------------------------------------------------------
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
        with self._connection() as connection:
            columns = self._table_columns(connection)
            clauses: list[str] = []
            params: list[Any] = []

            if category:
                clauses.append("LOWER(COALESCE(category, '')) = LOWER(%s)")
                params.append(category)
            if query:
                like = f"%{query}%"
                search = ["name ILIKE %s", "sku ILIKE %s"]
                params.extend([like, like])
                if "description" in columns:
                    search.append("description ILIKE %s")
                    params.append(like)
                if "category" in columns:
                    search.append("category ILIKE %s")
                    params.append(like)
                if "visual_tags" in columns:
                    search.append(
                        "EXISTS (SELECT 1 FROM unnest(visual_tags) AS tag WHERE tag ILIKE %s)"
                    )
                    params.append(like)
                clauses.append(f"({' OR '.join(search)})")
            if max_price is not None:
                clauses.append("price <= %s")
                params.append(float(max_price))
            if in_stock_only:
                clauses.append("stock > 0")

            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            order_by = SORT_ORDERS.get(sort, SORT_ORDERS["name"])
            sql = (
                f"SELECT {self._select_list(columns)} FROM {TABLE} {where} "
                f"ORDER BY {order_by} LIMIT %s OFFSET %s"
            )
            params.extend([limit, offset])
            rows = connection.execute(sql, params).fetchall()
        return [self._row_to_product(row) for row in rows]

    def get_product(self, identifier: str) -> Product | None:
        with self._connection() as connection:
            columns = self._table_columns(connection)
            row = connection.execute(
                f"SELECT {self._select_list(columns)} FROM {TABLE} "
                "WHERE product_id::text = %s OR LOWER(sku) = LOWER(%s)",
                (identifier, identifier),
            ).fetchone()
        return self._row_to_product(row) if row else None

    def similar_products(self, identifier: str, limit: int = 5) -> list[Product]:
        source = self.get_product(identifier)
        if source is None:
            return []

        with self._connection() as connection:
            columns = self._table_columns(connection)
            select_list = self._select_list(columns)

            if "img_embeddings" in columns:
                embedding_row = connection.execute(
                    f"SELECT img_embeddings::text AS embedding FROM {TABLE} WHERE product_id = %s",
                    (source.product_id,),
                ).fetchone()
                embedding = embedding_row["embedding"] if embedding_row else None
                if embedding:
                    try:
                        rows = connection.execute(
                            f"""
                            SELECT {select_list},
                                   1 - (img_embeddings <=> %s::vector) AS similarity
                            FROM {TABLE}
                            WHERE product_id <> %s AND img_embeddings IS NOT NULL
                            ORDER BY img_embeddings <=> %s::vector
                            LIMIT %s
                            """,
                            (embedding, source.product_id, embedding, limit),
                        ).fetchall()
                        return [
                            self._row_to_product(row, float(row["similarity"]))
                            for row in rows
                        ]
                    except Exception:  # pragma: no cover - pgvector optional
                        LOGGER.warning(
                            "Vector search failed for %s, falling back to tag similarity",
                            source.product_id,
                            exc_info=True,
                        )

            if "visual_tags" in columns and source.visual_tags:
                rows = connection.execute(
                    f"""
                    SELECT {select_list} FROM {TABLE}
                    WHERE product_id <> %s
                      AND (LOWER(COALESCE(category, '')) = LOWER(%s)
                           OR visual_tags && %s::text[])
                    LIMIT 200
                    """,
                    (source.product_id, source.category, source.visual_tags),
                ).fetchall()
            else:
                rows = connection.execute(
                    f"""
                    SELECT {select_list} FROM {TABLE}
                    WHERE product_id <> %s
                      AND LOWER(COALESCE(category, '')) = LOWER(%s)
                    LIMIT 200
                    """,
                    (source.product_id, source.category),
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
        with self._connection() as connection:
            columns = self._table_columns(connection)
            if "category" not in columns:
                return []
            rows = connection.execute(
                f"SELECT DISTINCT category FROM {TABLE} "
                "WHERE category IS NOT NULL ORDER BY category"
            ).fetchall()
        return [row["category"] for row in rows]

    def count(self) -> int:
        with self._connection() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS total FROM {TABLE}").fetchone()
        return int(row["total"])
