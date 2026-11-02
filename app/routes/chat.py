"""Assistant chat API."""

from __future__ import annotations

import re

from flask import Blueprint, jsonify

from app.errors import ValidationError
from app.routes import services
from app.routes._utils import json_body, text_field

chat_bp = Blueprint("chat", __name__)
USER_ID = re.compile(r"^[A-Za-z0-9._:@-]{1,128}$")
HISTORY_LIMIT = 20


@chat_bp.post("/chat")
def chat():
    payload = json_body()
    message = text_field(payload, "message", max_length=2000)
    user_id = text_field(payload, "user_id", default="web-demo", max_length=128)
    if not USER_ID.match(user_id):
        raise ValidationError("user_id contains unsupported characters")

    history = _history(payload.get("history"))
    result = services().assistant.reply(message, user_id=user_id, history=history)
    return jsonify(result)


def _history(raw) -> list[dict[str, str]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValidationError("history must be a list")
    history: list[dict[str, str]] = []
    for item in raw[-HISTORY_LIMIT:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        content = content.strip()[:2000]
        if content:
            history.append({"role": role, "content": content})
    return history
