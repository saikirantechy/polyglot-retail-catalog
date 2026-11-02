"""WSGI entry point used by gunicorn and Cloud Run."""

from app import create_app

app = create_app()
