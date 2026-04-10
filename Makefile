.PHONY: install test typecheck build clean release

install:
	uv sync

test:
	uv run pytest -v

typecheck:
	uv run mypy src/

build: clean
	uv run python -m build

clean:
	rm -rf dist/ build/ src/*.egg-info

release: test build
	uv run twine upload dist/*
