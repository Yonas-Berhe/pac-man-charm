# Pac-Man Backend Makefile

.PHONY: help install dev test lint clean

# Default target
help:
	@echo "Pac-Man Backend Commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make dev      - Run development server (port 3000)"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make clean    - Clean cache files"

# Install dependencies
install:
	uv sync

# Run development server
dev:
	uv run uvicorn main:app --reload --port 3000

# Run tests
test:
	uv run pytest tests/ -v

# Run tests with coverage
test-cov:
	uv run pytest tests/ -v --cov=app --cov-report=term-missing

# Run integration tests
test-integration:
	uv run pytest tests_integration/ -v

# Run all tests
test-all:
	uv run pytest tests/ tests_integration/ -v

# Run linter (requires ruff to be installed)
lint:
	uv run ruff check app/

# Format code
format:
	uv run ruff format app/

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
