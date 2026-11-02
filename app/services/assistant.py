"""Assistant facade with automatic fallback to local search."""

from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


class AssistantService:
    def __init__(self, rule_based: Any, gemini: Any | None = None) -> None:
        self.rule_based = rule_based
        self.gemini = gemini

    @property
    def backend_name(self) -> str:
        if self.gemini is not None and self.gemini.available:
            return self.gemini.backend_name
        return self.rule_based.backend_name

    def reply(
        self,
        message: str,
        *,
        user_id: str = "web-demo",
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        if self.gemini is not None and self.gemini.available:
            try:
                return self.gemini.reply(message, user_id=user_id, history=history)
            except Exception:
                LOGGER.exception("Gemini assistant failed; using local catalog search")
                result = self.rule_based.reply(message, user_id=user_id, history=history)
                result["mode"] = "fallback"
                result["notice"] = (
                    "Gemini was unavailable, so this answer came from local catalog search."
                )
                return result
        return self.rule_based.reply(message, user_id=user_id, history=history)
