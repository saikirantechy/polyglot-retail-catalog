"""Flask application factory for the Polyglot Store."""

from __future__ import annotations

import logging

from flask import Flask, jsonify, render_template, request

from .config import Settings
from .errors import ApiError
from .services.factory import build_services

LOGGER = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or Settings.from_env()

    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        MAX_CONTENT_LENGTH=1_048_576,
        SETTINGS=settings,
        JSON_SORT_KEYS=False,
    )
    app.json.sort_keys = False

    services = build_services(settings)
    app.extensions["services"] = services
    services.startup()

    from .routes.analytics import analytics_bp
    from .routes.chat import chat_bp
    from .routes.health import health_bp
    from .routes.interactions import interactions_bp
    from .routes.products import products_bp
    from .routes.web import web_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(interactions_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals() -> dict[str, object]:
        return {"mode": services.mode, "assistant_name": services.assistant.backend_name}

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        if request.path.startswith("/api/"):
            payload = {"error": error.message, "status": error.status}
            if error.details:
                payload["details"] = error.details
            return jsonify(payload), error.status
        return render_template("error.html", status=error.status, message=error.message), error.status

    @app.errorhandler(404)
    def handle_not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found", "status": 404}), 404
        return render_template("error.html", status=404, message="Page not found"), 404

    @app.errorhandler(500)
    def handle_server_error(_error):
        LOGGER.exception("Unhandled server error")
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error", "status": 500}), 500
        return render_template("error.html", status=500, message="Internal server error"), 500

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )

    LOGGER.info(
        "Polyglot Store started mode=%s catalog=%s interactions=%s analytics=%s assistant=%s",
        services.mode,
        services.catalog.name,
        services.interactions.name,
        services.analytics.name,
        services.assistant.backend_name,
    )
    return app
