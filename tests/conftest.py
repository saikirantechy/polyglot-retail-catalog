from __future__ import annotations

import pytest

from app import create_app
from app.config import Settings


@pytest.fixture()
def app(tmp_path):
    settings = Settings(
        secret_key="test-secret",
        demo_db_path=str(tmp_path / "demo.db"),
        force_demo=True,
        project_id="",
        alloydb_dsn="",
        mongodb_uri="",
        bigquery_project="",
    )
    application = create_app(settings)
    application.config.update(TESTING=True)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def services(app):
    return app.extensions["services"]
