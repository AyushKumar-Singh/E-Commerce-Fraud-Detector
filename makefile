.PHONY: help install train test lint format docker-build docker-up docker-down deploy clean

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.prod.yml

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Fraud Detector - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	$(PIP) install -r backend/requirements.txt
	$(PYTHON) -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

install-dev: install ## Install development dependencies
	$(PIP) install pytest pytest-cov black flake8 locust

setup-db: ## Initialize database
	docker-compose up -d db
	sleep 5
	docker-compose exec db psql -U postgres -d frauddb -f /docker-entrypoint-initdb.d/01-schema.sql

prepare-data: ## Run ETL to prepare training data
	$(PYTHON) scripts/prepare_data.py --type all

train: ## Train all models
	$(PYTHON) scripts/train_reviews.py
	$(PYTHON) scripts/train_tx.py

eval: ## Evaluate trained models
	$(PYTHON) scripts/eval.py

test: ## Run unit tests
	$(PYTEST) tests/ -v --cov=backend --cov-report=html --cov-report=term

test-integration: ## Run integration tests
	$(PYTEST) tests/ -v -m integration

test-load: ## Run load tests with Locust
	locust -f tests/load_test.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 60s

lint: ## Run code linting
	$(FLAKE8) backend/ --max-line-length=120 --exclude=__pycache__,*.pyc
	$(FLAKE8) scripts/ --max-line-length=120

format: ## Format code with Black
	$(BLACK) backend/ scripts/ tests/ --line-length=120

format-check: ## Check code formatting
	$(BLACK) backend/ scripts/ tests/ --line-length=120 --check

security-check: ## Run security vulnerability scan
	pip-audit
	bandit -r backend/ -ll

docker-build: ## Build Docker images
	$(DOCKER_COMPOSE) build

docker-up: ## Start development environment
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Services started:"
	@echo "   API: http://localhost:8000"
	@echo "   Dashboard: http://localhost:8000/dashboard"
	@echo "   Adminer: http://localhost:8080"

docker-down: ## Stop development environment
	$(DOCKER_COMPOSE) down

docker-logs: ## View Docker logs
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Remove all Docker containers and volumes
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

# Production targets
prod-build: ## Build production Docker images
	$(DOCKER_COMPOSE_PROD) build --no-cache

prod-up: ## Start production environment
	$(DOCKER_COMPOSE_PROD) up -d

prod-down: ## Stop production environment
	$(DOCKER_COMPOSE_PROD) down

prod-logs: ## View production logs
	$(DOCKER_COMPOSE_PROD) logs -f api

prod-scale: ## Scale API instances (usage: make prod-scale REPLICAS=4)
	$(DOCKER_COMPOSE_PROD) up -d --scale api=$(REPLICAS)

backup-db: ## Backup production database
	docker-compose exec db pg_dump -U postgres frauddb > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up to backups/"

restore-db: ## Restore database from backup (usage: make restore-db BACKUP=backup_file.sql)
	docker-compose exec -T db psql -U postgres frauddb < $(BACKUP)

migrate: ## Run database migrations
	docker-compose exec api alembic upgrade head

api-shell: ## Open shell in API container
	docker-compose exec api /bin/bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U postgres -d frauddb

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

generate-token: ## Generate new API token
	@$(PYTHON) -c "import secrets; print('API_TOKEN=' + secrets.token_urlsafe(32))"

ssl-cert: ## Generate SSL certificate with Let's Encrypt
	certbot certonly --standalone -d your-domain.com -d www.your-domain.com

monitoring: ## Open Grafana dashboard
	@echo "Opening Grafana: http://localhost:3000"
	@echo "Default credentials: admin / <GRAFANA_PASSWORD from .env>"

clean: ## Clean temporary files and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage build/ dist/

deploy-aws: ## Deploy to AWS (requires AWS CLI configured)
	@echo "🚀 Deploying to AWS ECS..."
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-ecr-repo>
	docker tag fraud-detector-api:latest <your-ecr-repo>/fraud-detector-api:latest
	docker push <your-ecr-repo>/fraud-detector-api:latest
	aws ecs update-service --cluster fraud-detector --service api --force-new-deployment

deploy-gcp: ## Deploy to Google Cloud Run
	@echo "🚀 Deploying to GCP Cloud Run..."
	gcloud builds submit --tag gcr.io/$(GCP_PROJECT_ID)/fraud-detector-api
	gcloud run deploy fraud-detector-api --image gcr.io/$(GCP_PROJECT_ID)/fraud-detector-api --platform managed --region us-central1

all: install train test docker-build ## Install, train, test, and build