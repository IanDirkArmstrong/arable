.PHONY: test test-unit test-integration coverage lint format install clean

# Install package in development mode
install:
	pip install -e .[dev]

# Run all tests
test:
	pytest

# Run only unit tests
test-unit:
	pytest -m "not integration"

# Run only integration tests
test-integration:
	pytest -m integration

# Run tests with coverage
coverage:
	pytest --cov=src/monday_automation --cov-report=html --cov-report=term

# Lint code
lint:
	flake8 src/ tests/
	black --check src/ tests/

# Format code
format:
	black src/ tests/

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete