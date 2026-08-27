.PHONY: help install dev test lint typecheck docker-up docker-down migrate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install
	cd apps/worker && pip install -r requirements.txt

dev: ## Start all services for development
	docker-compose up -d
	@echo "Services starting..."
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:3000"

test: ## Run all tests
	cd apps/api && python -m pytest ../../tests/ -v

lint: ## Run linting
	cd apps/api && ruff check .
	cd apps/web && npm run lint

typecheck: ## Run type checking
	cd apps/api && mypy app/
	cd apps/web && npm run type-check

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

migrate: ## Run database migrations
	cd apps/api && alembic upgrade head

seed: ## Seed database with initial data
	cd apps/api && python -m app.db.seed

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	rm -rf apps/web/.next
