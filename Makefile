.PHONY: install dev lint type test test-cov docs build clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

lint:
	ruff check bidiwave/ tests/

type:
	mypy bidiwave/

test:
	pytest tests/unit/ -c pyproject.toml -x -q

test-cov:
	pytest tests/unit/ -c pyproject.toml --cov=bidiwave --cov-report=term-missing

docs:
	mkdocs serve

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info/ .coverage .mypy_cache/ .pytest_cache/ .ruff_cache/ site/
