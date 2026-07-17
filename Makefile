.PHONY: install test lint typecheck build audit
install:
	python -m pip install -e '.[dev]'
test:
	pytest
lint:
	ruff check .
typecheck:
	mypy src/triageforge
build:
	python -m build
audit:
	triageforge audit . --fail-under 80
