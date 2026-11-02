"""BigQuery analytics repository."""

from __future__ import annotations

import logging
import re
from typing import Any

LOGGER = logging.getLogger(__name__)

IDENTIFIER = re.compile(r"^[A-Za-z0-9_]+$")


def _safe_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.match(value):
        raise ValueError(f"Invalid BigQuery {label}: {value!r}")
    return value


class BigQueryAnalyticsRepository:
    name = "bigquery"
    enabled = True

    def __init__(self, project: str, dataset: str, table: str) -> None:
        self.project = _safe_identifier(project, "project")
        self.dataset = _safe_identifier(dataset, "dataset")
        self.table = _safe_identifier(table, "table")
        self._client: Any = None

    @property
    def table_id(self) -> str:
        return f"{self.project}.{self.dataset}.{self.table}"

    def _bigquery(self) -> Any:
        if self._client is None:
            try:
                from google.cloud import bigquery
            except ImportError as exc:  # pragma: no cover - depends on environment
                raise RuntimeError(
                    "google-cloud-bigquery is required for BigQuery mode. "
                    "Install requirements-cloud.txt or unset BIGQUERY_PROJECT."
                ) from exc
            self._client = bigquery.Client(project=self.project)
        return self._client

    def top_products(self, limit: int = 5) -> list[dict[str, Any]]:
        from google.cloud import bigquery

        query = f"""
            SELECT product_id,
                   SUM(interaction_score) AS score,
                   COUNT(*) AS events
            FROM `{self.table_id}`
            GROUP BY product_id
            ORDER BY score DESC, events DESC
            LIMIT @limit
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", limit)]
        )
        rows = self._bigquery().query(query, job_config=job_config).result()
        return [
            {
                "product_id": row["product_id"],
                "score": round(float(row["score"] or 0), 2),
                "events": int(row["events"] or 0),
            }
            for row in rows
        ]

    def summary(self) -> dict[str, Any]:

        query = f"""
            SELECT COUNT(*) AS rows,
                   COALESCE(SUM(interaction_score), 0) AS score
            FROM `{self.table_id}`
        """
        row = next(iter(self._bigquery().query(query).result()), None)
        if row is None:
            return {"interaction_rows": 0, "total_score": 0.0, "by_event": {}}

        by_event_query = f"""
            SELECT interaction_score AS bucket, COUNT(*) AS events
            FROM `{self.table_id}`
            GROUP BY bucket
            ORDER BY bucket
        """
        by_event = {
            str(item["bucket"]): int(item["events"])
            for item in self._bigquery().query(by_event_query).result()
        }
        return {
            "interaction_rows": int(row["rows"] or 0),
            "total_score": round(float(row["score"] or 0), 2),
            "by_event": by_event,
        }


class DisabledAnalyticsRepository:
    name = "disabled"
    enabled = False

    def top_products(self, limit: int = 5) -> list[dict[str, Any]]:
        return []

    def summary(self) -> dict[str, Any]:
        return {"interaction_rows": 0, "total_score": 0.0, "by_event": {}}
