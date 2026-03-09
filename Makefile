.PHONY: dev test lint check fix migrate migrate-down frontend-dev

dev:
	docker compose up -d

test:
	pytest tests/ -v

lint:
	ruff check backend/src/ && ruff format --check backend/src/

fix:
	ruff check backend/src/ --fix && ruff format backend/src/

check: lint test

migrate:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

frontend-dev:
	cd frontend && npm run dev
