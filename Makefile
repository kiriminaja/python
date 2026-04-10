UV := python3 -m uv

.PHONY: install test typecheck build clean release

install:
	$(UV) sync

test:
	$(UV) run pytest -v

typecheck:
	$(UV) run mypy src/

build: clean
	$(UV) run python -m build

clean:
	rm -rf dist/ build/ src/*.egg-info

release: test build
	$(UV) run twine upload dist/*
