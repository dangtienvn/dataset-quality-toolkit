.PHONY: dev test lint check fix migrate migrate-down migrate-create frontend-dev

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
	cd backend && uv run alembic upgrade head

migrate-down:
	cd backend && uv run alembic downgrade -1

migrate-create:
	cd backend && uv run alembic revision --autogenerate -m "$(msg)"

frontend-dev:
	cd frontend && npm run dev
