"""Composition root: build repositories and services from settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import Settings
from app.repositories import (
    BigQueryAnalyticsRepository,
    DemoRepository,
    MongoRepository,
    PostgresCatalogRepository,
)
from app.repositories.bigquery_analytics import DisabledAnalyticsRepository
from app.services.analytics import AnalyticsService
from app.services.assistant import AssistantService
from app.services.catalog import CatalogService
from app.services.gemini_assistant import GeminiAssistant
from app.services.interactions import InteractionService
from app.services.rule_assistant import RuleBasedAssistant


@dataclass
class Services:
    settings: Settings
    catalog: CatalogService
    interactions: InteractionService
    analytics: AnalyticsService
    assistant: AssistantService
    mode: str
    demo: DemoRepository | None = None

    def startup(self) -> None:
        if self.demo is not None:
            self.demo.initialise()

    def backends(self) -> dict[str, str]:
        return {
            "catalog": self.catalog.name,
            "interactions": self.interactions.name,
            "analytics": self.analytics.name,
            "assistant": self.assistant.backend_name,
        }


def build_services(settings: Settings) -> Services:
    mongo: MongoRepository | None = None
    if settings.use_mongodb:
        mongo = MongoRepository(settings.mongodb_uri, settings.mongodb_database)

    demo = DemoRepository(settings.demo_db_file)
    demo_used = not settings.use_alloydb or not settings.use_mongodb or not (
        settings.use_bigquery or settings.use_mongodb
    )

    if settings.use_alloydb:
        catalog_repository: Any = PostgresCatalogRepository(
            settings.alloydb_dsn, attributes_provider=mongo
        )
    else:
        catalog_repository = demo

    interaction_repository: Any = mongo if mongo is not None else demo

    if settings.use_bigquery:
        analytics_repository: Any = BigQueryAnalyticsRepository(
            settings.bigquery_project,
            settings.bigquery_dataset,
            settings.bigquery_table,
        )
    elif mongo is not None:
        analytics_repository = mongo
    elif demo_used:
        analytics_repository = demo
    else:  # pragma: no cover - unreachable, kept for clarity
        analytics_repository = DisabledAnalyticsRepository()

    catalog = CatalogService(catalog_repository)
    interactions = InteractionService(interaction_repository, catalog)
    analytics = AnalyticsService(analytics_repository, interaction_repository, catalog)

    rule_based = RuleBasedAssistant(catalog, interactions, analytics)
    gemini = GeminiAssistant(settings, catalog, interactions, analytics)
    assistant = AssistantService(rule_based, gemini)

    return Services(
        settings=settings,
        catalog=catalog,
        interactions=interactions,
        analytics=analytics,
        assistant=assistant,
        mode=settings.mode,
        demo=demo if demo_used else None,
    )
