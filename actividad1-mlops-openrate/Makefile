.PHONY: install sync test test-unit test-integration run clean

install:
	uv sync

test:
	uv run pytest

test-unit:
	uv run pytest tests/unit/

test-integration:
	uv run pytest tests/integration/

run:
	uv run src/main.py

clean:
	rm -rf .pytest_cache __pycache__
