.PHONY: dev test lint check fix migrate migrate-down frontend-dev

dev:
	docker compose up -d

test:
	uv run pytest tests/ -v --cov --cov-report=term-missing

lint:
	uv run ruff check backend/src/ && uv run ruff format --check backend/src/

fix:
	uv run ruff check backend/src/ --fix && uv run ruff format backend/src/

check: lint test

migrate:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

frontend-dev:
	cd frontend && npm run dev
