# Persona Makefile
# Unified task runner for development, testing, and deployment
#
# Usage: make [target]
# Run 'make help' to see all available targets

.PHONY: help install dev test lint format type-check check security pii-scan docs docs-build docs-serve clean

# Default Python - override with: make PYTHON=python3.13 test
PYTHON ?= python3

# Colours for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# Default target
.DEFAULT_GOAL := help

##@ General

help: ## Show this help message
	@echo "Persona Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Install production dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .
	@echo "$(GREEN)Production dependencies installed$(NC)"

dev: ## Install all development dependencies and pre-commit hooks
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[all]"
	pre-commit install
	@echo "$(GREEN)Development environment ready$(NC)"

##@ Quality Assurance

test: ## Run tests with coverage
	pytest tests/ --cov=src/persona --cov-report=term-missing -m "not real_api"

test-all: ## Run all tests including real API tests
	pytest tests/ --cov=src/persona --cov-report=term-missing

lint: ## Run ruff linter
	ruff check src/ tests/

format: ## Format code with ruff
	ruff format src/ tests/

format-check: ## Check code formatting without changes
	ruff format --check src/ tests/

type-check: ## Run mypy type checker
	mypy src/persona --ignore-missing-imports

check: lint type-check test ## Run all quality checks (lint, type-check, test)
	@echo "$(GREEN)All checks passed$(NC)"

##@ Security

security: ## Run security scans (bandit + safety)
	bandit -r src/persona -ll
	safety check || true
	@echo "$(GREEN)Security scan complete$(NC)"

pii-scan: ## Scan for personally identifiable information
	./scripts/pii_scan.sh

##@ Documentation

docs: docs-serve ## Serve documentation with live reload (alias)

docs-serve: ## Serve documentation with live reload
	mkdocs serve

docs-build: ## Build documentation site
	mkdocs build --strict

##@ Docker

docker-build: ## Build production Docker image
	docker build -t persona:latest .

docker-build-dev: ## Build development Docker image
	docker build -f Dockerfile.dev -t persona:dev .

docker-up: ## Start production containers
	docker compose up -d

docker-down: ## Stop containers
	docker compose down

docker-dev: ## Start development containers
	docker compose -f docker-compose.dev.yml up -d

docker-logs: ## View container logs
	docker compose logs -f

##@ Maintenance

clean: ## Remove build artefacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf site/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.bak" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleaned build artefacts$(NC)"

reset: clean ## Full reset: clean + remove venv
	rm -rf .venv/
	@echo "$(YELLOW)Virtual environment removed. Run 'make dev' to recreate.$(NC)"

##@ Release

version: ## Show current version
	@grep -m1 'version = ' pyproject.toml | cut -d'"' -f2

release-check: check pii-scan ## Run all pre-release checks
	@echo "$(GREEN)Pre-release checks passed$(NC)"
