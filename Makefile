.PHONY: help install test lint format clean run docker demo benchmark docs

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)ClearCraft - Available Make Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Installation & Setup
install: ## Install dependencies and setup environment
	@echo "$(BLUE)Installing ClearCraft...$(NC)"
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && python -m spacy download en_core_web_sm
	cp -n .env.sample .env || true
	@echo "$(GREEN)✓ Installation complete!$(NC)"
	@echo "$(YELLOW)Run 'source venv/bin/activate' to activate the virtual environment$(NC)"

install-dev: install ## Install with development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	. venv/bin/activate && pip install pytest pytest-cov pytest-asyncio ruff mypy types-pyyaml types-markdown
	@echo "$(GREEN)✓ Development environment ready!$(NC)"

# Development
run: ## Run the development server
	@echo "$(BLUE)Starting ClearCraft server...$(NC)"
	. venv/bin/activate && clearcraft server --reload

run-prod: ## Run the production server
	@echo "$(BLUE)Starting ClearCraft in production mode...$(NC)"
	. venv/bin/activate && clearcraft server

demo: ## Run the interactive demo
	@echo "$(BLUE)Running ClearCraft demo...$(NC)"
	. venv/bin/activate && python examples/demo.py

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	. venv/bin/activate && python examples/benchmark.py

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	. venv/bin/activate && pytest -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	. venv/bin/activate && pytest --cov=clearcraft --cov-report=term --cov-report=html
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	. venv/bin/activate && pytest-watch

integration-test: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	. venv/bin/activate && python tests/integration_test.py

# Code Quality
lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	. venv/bin/activate && ruff check clearcraft/ tests/ examples/

lint-fix: ## Auto-fix linting issues
	@echo "$(BLUE)Auto-fixing linting issues...$(NC)"
	. venv/bin/activate && ruff check --fix clearcraft/ tests/ examples/

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	. venv/bin/activate && ruff format clearcraft/ tests/ examples/
	@echo "$(GREEN)✓ Code formatted!$(NC)"

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	. venv/bin/activate && mypy clearcraft/

quality: lint typecheck test ## Run all quality checks
	@echo "$(GREEN)✓ All quality checks passed!$(NC)"

# Docker
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t clearcraft:latest .
	@echo "$(GREEN)✓ Docker image built!$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -d -p 8000:8000 --name clearcraft clearcraft:latest
	@echo "$(GREEN)✓ Container running at http://localhost:8000$(NC)"

docker-stop: ## Stop Docker container
	@echo "$(BLUE)Stopping Docker container...$(NC)"
	docker stop clearcraft || true
	docker rm clearcraft || true
	@echo "$(GREEN)✓ Container stopped$(NC)"

docker-compose-up: ## Start with docker-compose
	@echo "$(BLUE)Starting with docker-compose...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services running at http://localhost:8000$(NC)"

docker-compose-down: ## Stop docker-compose services
	@echo "$(BLUE)Stopping docker-compose services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-compose-logs: ## View docker-compose logs
	docker-compose logs -f

# Documentation
docs: ## Open documentation in browser
	@echo "$(BLUE)Opening documentation...$(NC)"
	@command -v xdg-open > /dev/null && xdg-open README.md || open README.md

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Starting documentation server...$(NC)"
	. venv/bin/activate && python -m http.server 8080 -d .

# Analysis & Rewriting (CLI)
analyze: ## Analyze a text file (usage: make analyze FILE=path/to/file.txt)
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make analyze FILE=path/to/file.txt$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Analyzing $(FILE)...$(NC)"
	. venv/bin/activate && clearcraft analyze --file $(FILE)

rewrite: ## Rewrite a text file (usage: make rewrite FILE=input.txt OUTPUT=output.txt)
	@if [ -z "$(FILE)" ] || [ -z "$(OUTPUT)" ]; then \
		echo "$(YELLOW)Usage: make rewrite FILE=input.txt OUTPUT=output.txt$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Rewriting $(FILE) to $(OUTPUT)...$(NC)"
	. venv/bin/activate && clearcraft rewrite --file $(FILE) --output $(OUTPUT)

# Cleanup
clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '.coverage' -delete
	rm -rf build/ dist/
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

clean-cache: ## Clean model cache
	@echo "$(BLUE)Cleaning model cache...$(NC)"
	rm -rf .cache/
	@echo "$(GREEN)✓ Cache cleaned!$(NC)"

clean-all: clean clean-cache ## Clean everything including venv
	@echo "$(BLUE)Removing virtual environment...$(NC)"
	rm -rf venv/
	@echo "$(GREEN)✓ Complete cleanup done!$(NC)"

# Version & Release
version: ## Show version information
	@echo "$(BLUE)ClearCraft Version Information:$(NC)"
	@. venv/bin/activate && clearcraft version

# Health Check
health: ## Check service health
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -f http://localhost:8000/healthz && echo "$(GREEN)✓ Service is healthy$(NC)" || echo "$(YELLOW)⚠ Service is not running$(NC)"

# Quick Examples
example-analyze: ## Analyze sample academic text
	@echo "$(BLUE)Analyzing sample academic text...$(NC)"
	. venv/bin/activate && clearcraft analyze --file examples/sample_academic.txt

example-rewrite: ## Rewrite sample blog text
	@echo "$(BLUE)Rewriting sample blog text...$(NC)"
	. venv/bin/activate && clearcraft rewrite --file examples/sample_blog.txt --tone conversational

# CI/CD Simulation
ci: quality ## Run CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline passed!$(NC)"

# All-in-one commands
setup: install-dev ## Complete setup for new developers
	@echo "$(GREEN)✓ Development environment fully configured!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. source venv/bin/activate"
	@echo "  2. make run"
	@echo "  3. Visit http://localhost:8000"

verify: quality integration-test ## Verify complete installation
	@echo "$(GREEN)✓ Installation verified successfully!$(NC)"
