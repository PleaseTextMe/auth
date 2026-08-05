.PHONY: up down build logs shell db-shell redis-shell migrate generate help

# Default values
DC = docker compose
APP_CONTAINER = please_text_me_auth
DB_CONTAINER = please_text_me_postgres
REDIS_CONTAINER = please_text_me_redis

help:
	@echo "Available commands:"
	@echo "  make up          - Start all containers in background"
	@echo "  make down        - Stop and remove all containers"
	@echo "  make build       - Rebuild the auth app image"
	@echo "  make logs        - Tail logs of all containers"
	@echo "  make shell       - Open a shell inside the auth app container"
	@echo "  make db-shell    - Open psql inside the postgres container"
	@echo "  make redis-shell - Open redis-cli inside the redis container"
	@echo "  make migrate     - Run Alembic migrations to head"
	@echo "  make generate    - Generate a new Alembic migration (usage: make generate m=\"message\")"

up:
	$(DC) up -d

down:
	$(DC) down

build:
	$(DC) build

logs:
	$(DC) logs -f

shell:
	docker exec -it $(APP_CONTAINER) /bin/sh

db-shell:
	docker exec -it $(DB_CONTAINER) psql -U postgres -d please_text_me_db

redis-shell:
	docker exec -it $(REDIS_CONTAINER) redis-cli

migrate:
	docker exec -it $(APP_CONTAINER) /bin/sh -c "PYTHONPATH=. alembic upgrade head"

generate:
	@if [ -z "$(m)" ]; then \
		echo "Error: Migration message is required. Usage: make generate m=\"migration message\""; \
		exit 1; \
	fi
	docker exec -it $(APP_CONTAINER) /bin/sh -c "PYTHONPATH=. alembic revision --autogenerate -m '$(m)'"
