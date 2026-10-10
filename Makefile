.PHONY: up down logs ps migrate test backend-test backend-lint frontend-lint frontend-build

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f backend

ps:
	docker compose ps

migrate:
	docker compose exec backend alembic upgrade head

test: backend-test frontend-lint

backend-test:
	docker compose exec backend pytest

backend-lint:
	docker compose exec backend ruff check .

frontend-lint:
	docker compose exec frontend npm run lint

frontend-build:
	docker compose exec frontend npm run build