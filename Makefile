.PHONY: help install dev build test test-backend test-frontend lint run docker-build docker-run clean

help:
	@echo "ScoutAI - AI Competitor & Market Research Agent"
	@echo ""
	@echo "Targets:"
	@echo "  install         Install backend & frontend dependencies"
	@echo "  dev             Run backend and frontend concurrently in development"
	@echo "  build           Build frontend assets and install backend"
	@echo "  test            Run all backend and frontend tests"
	@echo "  test-backend    Run pytest backend test suite"
	@echo "  test-frontend   Run vitest frontend component tests"
	@echo "  lint            Run ruff and prettier/eslint checks"
	@echo "  run             Run the production FastAPI app serving built React SPA"
	@echo "  docker-build    Build production Docker container image"
	@echo "  docker-run      Run Docker container locally"
	@echo "  clean           Clean build artifacts and temporary databases"

install:
	python -m pip install -e ./backend
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@echo "Start backend: uvicorn backend.app.main:app --reload --port 8000"
	@echo "Start frontend: cd frontend && npm run dev"

build:
	cd frontend && npm run build
	python -m pip install -e ./backend

test-backend:
	pytest -v backend/tests

test-frontend:
	cd frontend && npx vitest run

test: test-backend test-frontend

lint:
	ruff check backend
	ruff format --check backend

run:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t scoutai:latest .

docker-run:
	docker run -p 8000:8000 --env DEMO_MODE=true scoutai:latest

clean:
	rm -rf frontend/dist backend/__pycache__ .pytest_cache scoutai.db
