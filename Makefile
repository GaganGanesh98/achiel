.PHONY: dev-backend dev-frontend dev-db migrate migration

dev-db:
	docker compose up -d

dev-backend:
	cd backend && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

migrate:
	cd backend && uv run alembic upgrade head

migration:
	cd backend && uv run alembic revision --autogenerate -m "$(name)"

test:
	cd backend && uv run pytest -q

seed-domains:
	cd backend && uv run python scripts/seed_allowed_domains.py
