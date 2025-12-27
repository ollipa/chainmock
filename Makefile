
color := $(shell tput setaf 2)
off := $(shell tput sgr0)
PYTHON := $(if $(shell command -v python3),python3,python)
TARGETS = src tests

.PHONY: all
all: lint test

.PHONY: lint
lint: format linter typecheck

.PHONY: test
test: docs coverage

.PHONY: coverage
coverage:
# Remove any leftover coverage files before running tests
	@uv run coverage combine --quiet > /dev/null || true

	@printf '\n\n*****************\n'
	@printf '$(color)Running doctest$(off)\n'
	@printf '*****************\n'
	uv run coverage run --parallel-mode --source chainmock tests/integrations/i_doctest.py

	@printf '\n\n*****************\n'
	@printf '$(color)Running pytest$(off)\n'
	@printf '*****************\n'
	uv run coverage run --parallel-mode --source chainmock -m pytest tests/integrations/i_pytest.py

	@printf '\n\n*****************\n'
	@printf '$(color)Running unittest$(off)\n'
	@printf '*****************\n'
	PYTHONPATH=./ uv run coverage run --parallel-mode --source chainmock tests/integrations/i_unittest.py 2> /dev/null

	@printf '\n\n*****************\n'
	@printf '$(color)Test coverage$(off)\n'
	@printf '*****************\n'
	@uv run coverage combine --quiet
	uv run coverage report --fail-under=100 --show-missing

.PHONY: typecheck
typecheck:
	@printf '\n\n*****************\n'
	@printf '$(color)Running type checker$(off)\n'
	@printf '*****************\n'
	uv run ty check ${TARGETS}

.PHONY: format
format:
	@printf '\n\n*****************\n'
	@printf '$(color)Running format$(off)\n'
	@printf '*****************\n'
	uv run ruff format --check ${TARGETS}

.PHONY: linter
linter:
	@printf '\n\n*****************\n'
	@printf '$(color)Running linter$(off)\n'
	@printf '*****************\n'
	uv run ruff check ${TARGETS}

.PHONY: docs
docs:
	@printf '\n\n*****************\n'
	@printf '$(color)Test building docs$(off)\n'
	@printf '*****************\n'
	uv run mkdocs build --strict

.PHONY: serve
serve:
	uv run mkdocs serve --open
