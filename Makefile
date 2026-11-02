.PHONY: install install-cloud install-dev run test lint docker up down clean

install:
	python -m pip install -r requirements.txt

install-cloud:
	python -m pip install -r requirements-cloud.txt

install-dev:
	python -m pip install -r requirements-dev.txt

run:
	python -m app

test:
	python -m pytest

lint:
	python -m ruff check .

docker:
	docker build -t polyglot-retail-catalog .

up:
	docker compose up --build

down:
	docker compose down

clean:
	rm -rf instance .pytest_cache .ruff_cache __pycache__ app/__pycache__
