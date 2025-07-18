# Makefile for Inverted Index Search API
# Usage: make [target]

.PHONY: help install test test-unit test-integration test-coverage run demo clean docker-build docker-run docker-stop lint format check

# Variables
PYTHON = python3
PIP = pip3
APP_MODULE = app.main
TEST_DIR = tests
COVERAGE_DIR = htmlcov

# Default target
help:
	@echo "Inverted Index Search API - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install          Install dependencies"
	@echo "  run              Run the API server"
	@echo "  demo             Run the demo script"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code with black"
	@echo "  check            Run all code quality checks"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run with Docker Compose"
	@echo "  docker-stop      Stop Docker containers"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean up generated files"
	@echo "  requirements     Generate requirements.txt"

# Development
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "Installation complete!"

run:
	@echo "Starting Inverted Index Search API..."
	$(PYTHON) -m $(APP_MODULE)

demo:
	@echo "Running demo..."
	./scripts/demo.sh

# Testing
test:
	@echo "Running all tests..."
	./scripts/run_tests.sh

test-unit:
	@echo "Running unit tests..."
	./scripts/run_tests.sh -t unit -v

test-integration:
	@echo "Running integration tests..."
	./scripts/run_tests.sh -t integration -v

test-coverage:
	@echo "Running tests with coverage..."
	./scripts/run_tests.sh -c -v

# Code Quality
lint:
	@echo "Running linting checks..."
	@if command -v flake8 > /dev/null; then \
		flake8 app/ tests/ --max-line-length=88 --ignore=E203,W503; \
	else \
		echo "flake8 not installed. Install with: pip install flake8"; \
		exit 1; \
	fi

format:
	@echo "Formatting code..."
	@if command -v black > /dev/null; then \
		black app/ tests/; \
	else \
		echo "black not installed. Install with: pip install black"; \
		exit 1; \
	fi

check: lint format test
	@echo "All code quality checks passed!"

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t inverted-index-api .

docker-run:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# Utilities
clean:
	@echo "Cleaning up generated files..."
	rm -rf __pycache__/
	rm -rf app/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf $(COVERAGE_DIR)/
	rm -rf .coverage
	rm -rf data/
	rm -rf *.egg-info/
	rm -rf dist/
	rm -rf build/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Cleanup complete!"

requirements:
	@echo "Generating requirements.txt..."
	$(PIP) freeze > requirements.txt
	@echo "requirements.txt updated!"

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	@if ! command -v black > /dev/null; then \
		echo "Installing development tools..."; \
		$(PIP) install black flake8 pytest-cov; \
	fi
	@echo "Development setup complete!"

# Quick start for new users
quickstart: dev-setup
	@echo "Starting API for quick testing..."
	@echo "API will be available at: http://localhost:8000"
	@echo "API docs will be available at: http://localhost:8000/docs"
	@echo "Press Ctrl+C to stop"
	$(PYTHON) -m $(APP_MODULE)

# Production deployment
deploy-check: test check
	@echo "All deployment checks passed!"

# Performance testing
benchmark:
	@echo "Running performance benchmark..."
	@if command -v pytest-benchmark > /dev/null; then \
		pytest tests/ --benchmark-only; \
	else \
		echo "pytest-benchmark not installed. Install with: pip install pytest-benchmark"; \
	fi

# Documentation
docs:
	@echo "Generating documentation..."
	@if command -v pdoc3 > /dev/null; then \
		pdoc3 --html app/ --output-dir docs/; \
	else \
		echo "pdoc3 not installed. Install with: pip install pdoc3"; \
	fi

# Security check
security:
	@echo "Running security checks..."
	@if command -v bandit > /dev/null; then \
		bandit -r app/; \
	else \
		echo "bandit not installed. Install with: pip install bandit"; \
	fi 