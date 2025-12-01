.PHONY: help install format lint test develop clean

UV := uv

help:
	@echo "Available targets:"
	@echo "  install   Install project and dev dependencies with uv sync"
	@echo "  format    Format code with ruff"
	@echo "  lint      Run ruff, mypy, and bandit"
	@echo "  test      Run test suite"
	@echo "  develop   Launch Home Assistant dev instance"
	@echo "  clean     Remove build artefacts"

install:
	$(UV) sync --frozen --dev

format:
	$(UV) run ruff format custom_components tests scripts

lint:
	$(UV) run ruff check custom_components tests scripts
	$(UV) run mypy custom_components
	$(UV) run bandit -r custom_components

test:
	$(UV) run pytest

develop:
	./scripts/develop

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
