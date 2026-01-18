.PHONY: help install install-dev setup run run-dev test lint format clean docker-up docker-down docker-logs db-init db-reset

help:
	@echo "Enterprise Knowledge RAG - Development Commands"
	@echo ""
	@echo "Setup & Install:"
	@echo "  make install          - Install dependencies"
	@echo "  make install-dev      - Install dependencies + dev tools"
	@echo "  make setup            - Full setup (install + docker + db)"
	@echo ""
	@echo "Running:"
	@echo "  make run              - Run production server"
	@echo "  make run-dev          - Run development server with reload"
	@echo "  make worker           - Start Celery worker"
	@echo ""
	@echo "Testing & Code Quality:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make lint             - Run linters (ruff, mypy)"
	@echo "  make format           - Format code with black"
	@echo "  make format-check     - Check code formatting"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        - Start Docker services"
	@echo "  make docker-down      - Stop Docker services"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docker-build     - Build Docker image"
	@echo ""
	@echo "Database:"
	@echo "  make db-init          - Initialize database"
	@echo "  make db-reset         - Reset database (WARNING: deletes all data)"
	@echo "  make db-migrate       - Run migrations"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove build artifacts and cache"
	@echo "  make clean-all        - Clean + remove virtual environment"

# Installation targets
install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip setuptools wheel
	pip install -e ".[dev]"

setup: install docker-up db-init
	@echo "✓ Setup complete! Run 'make run-dev' to start the server"

# Running targets
run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

run-dev:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

worker:
	celery -A app.tasks worker --loglevel=info

worker-beat:
	celery -A app.tasks beat --loglevel=info

# Testing targets
test:
	pytest -v

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

# Code quality targets
lint:
	ruff check app
	mypy app

format:
	black app tests

format-check:
	black --check app tests

# Docker targets
docker-up:
	docker-compose up -d
	@echo "✓ Docker services started"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Redis: localhost:6379"
	@echo "  Weaviate: localhost:8080"
	@echo "  Prometheus: localhost:9090"
	@echo "  Grafana: localhost:3000"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker build -t enterprise-rag:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env enterprise-rag:latest

# Database targets
db-init:
	python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"

db-reset:
	python -c "from app.database import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"
	@echo "✓ Database reset complete"

db-migrate:
	alembic upgrade head

# Cleanup targets
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf build dist .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	@echo "✓ Cleanup complete"

clean-all: clean
	rm -rf venv/
	@echo "✓ Full cleanup complete"

# Development utilities
freeze:
	pip freeze > requirements-lock.txt

env-setup:
	cp .env.example .env
	@echo "✓ Created .env file from template (edit with your config)"

logs:
	tail -f logs/*.log

check: format-check lint test
	@echo "✓ All checks passed!"
