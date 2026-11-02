"""Application settings sourced from environment variables.

The app supports three operating modes:

* ``demo``   - no cloud services configured; SQLite + rule-based assistant.
* ``hybrid`` - some cloud services configured, the rest fall back to demo.
* ``cloud``  - AlloyDB, MongoDB and BigQuery are all configured.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # python-dotenv is a base dependency, but never fail hard without it.
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - defensive
    def load_dotenv(*_args, **_kwargs):
        return False


DEFAULT_DEMO_DB = "instance/demo.db"
DEFAULT_DATASET = "ecommerce_analytics"
DEFAULT_TABLE = "user_product_interactions"
DEFAULT_MODEL = "gemini-2.5-flash"


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    return default


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    project_id: str = ""
    project_number: str = ""
    region: str = "us-central1"
    secret_key: str = "dev-only-change-me"

    alloydb_dsn: str = ""
    mongodb_uri: str = ""
    mongodb_database: str = "ecommerce_db"

    bigquery_project: str = ""
    bigquery_dataset: str = DEFAULT_DATASET
    bigquery_table: str = DEFAULT_TABLE

    mcp_toolbox_url: str = ""
    google_cloud_location: str = "us-central1"
    gemini_model: str = DEFAULT_MODEL

    demo_db_path: str = DEFAULT_DEMO_DB
    force_demo: bool = False
    max_products: int = 100

    @classmethod
    def from_env(cls, *, load_file: bool = True) -> Settings:
        if load_file:
            load_dotenv(override=False)

        project_id = _env("GOOGLE_CLOUD_PROJECT", "PROJECT_ID")
        dsn = _env("ALLOYDB_DSN")
        if not dsn:
            host = _env("ALLOYDB_HOST")
            if host:
                user = _env("ALLOYDB_USER", default="postgres")
                password = _env("ALLOYDB_PASSWORD")
                port = _env("ALLOYDB_PORT", default="5432")
                database = _env("ALLOYDB_DATABASE", default="postgres")
                credentials = f"{user}:{password}@" if password else f"{user}@"
                dsn = f"postgresql://{credentials}{host}:{port}/{database}"

        return cls(
            project_id=project_id,
            project_number=_env("PROJECT_NUMBER"),
            region=_env("REGION", default="us-central1"),
            secret_key=_env("SECRET_KEY", default="dev-only-change-me"),
            alloydb_dsn=dsn,
            mongodb_uri=_env("MONGODB_URI"),
            mongodb_database=_env("MONGODB_DB", default="ecommerce_db"),
            bigquery_project=_env("BIGQUERY_PROJECT"),
            bigquery_dataset=_env("BIGQUERY_DATASET", default=DEFAULT_DATASET),
            bigquery_table=_env("BIGQUERY_TABLE", default=DEFAULT_TABLE),
            mcp_toolbox_url=_env("MCP_TOOLBOX_URL", "MCP_TOOLBOX_SERVER_URL"),
            google_cloud_location=_env("GOOGLE_CLOUD_LOCATION", default="us-central1"),
            gemini_model=_env("MODEL", "GEMINI_MODEL", default=DEFAULT_MODEL),
            demo_db_path=_env("DEMO_DB_PATH", default=DEFAULT_DEMO_DB),
            force_demo=_env_bool("DEMO_MODE", False),
        )

    @property
    def use_alloydb(self) -> bool:
        return not self.force_demo and bool(self.alloydb_dsn)

    @property
    def use_mongodb(self) -> bool:
        return not self.force_demo and bool(self.mongodb_uri)

    @property
    def use_bigquery(self) -> bool:
        return not self.force_demo and bool(self.bigquery_project)

    @property
    def mode(self) -> str:
        cloud = [self.use_alloydb, self.use_mongodb, self.use_bigquery]
        if not any(cloud):
            return "demo"
        if all(cloud):
            return "cloud"
        return "hybrid"

    @property
    def demo_db_file(self) -> Path:
        return Path(self.demo_db_path)

    @property
    def gemini_enabled(self) -> bool:
        return not self.force_demo and bool(self.project_id)
