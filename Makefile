ENV_FILE ?= .env
CONFIG_ENV_FILE ?= .env.example

.PHONY: setup storage-bootstrap compose-config compose-config-gpu build up up-gpu down logs migrate seed test test-backend test-cv test-frontend test-training

setup: storage-bootstrap

storage-bootstrap:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1

compose-config:
	docker compose --env-file $(CONFIG_ENV_FILE) config

compose-config-gpu:
	docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file $(CONFIG_ENV_FILE) config

build:
	docker compose --env-file $(ENV_FILE) build

up:
	docker compose --env-file $(ENV_FILE) up --build

up-gpu:
	docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file $(ENV_FILE) up --build

down:
	docker compose --env-file $(ENV_FILE) down

logs:
	docker compose --env-file $(ENV_FILE) logs -f

migrate:
	docker compose --env-file $(ENV_FILE) run --rm backend alembic upgrade head

seed:
	docker compose --env-file $(ENV_FILE) run --rm backend python -m app.setup

test: test-backend test-cv test-frontend test-training

test-backend:
	cd backend && python -m pytest

test-cv:
	cd cv && python -m pytest

test-frontend:
	cd frontend && npm test

test-training:
	python -m pytest training/tests
