
color := $(shell tput setaf 2)
off := $(shell tput sgr0)
PYTHON := $(if $(shell command -v python3),python3,python)
TARGETS = src tests

.PHONY: all
all: lint test

.PHONY: lint
lint: isort black mypy pylint

.PHONY: test
test: install docs coverage

.PHONY: install
install:
	@printf '\n\n*****************\n'
	@printf '$(color)Installing package$(off)\n'
	@printf '*****************\n'
ifeq (${VIRTUAL_ENV},)
	@printf 'Skipping install. VIRTUAL_ENV is not set.\n'
else
	poetry run pip install --quiet .
endif

.PHONY: coverage
coverage:
# Remove any leftover coverage files before running tests
	@poetry run coverage combine --quiet > /dev/null || true

	@printf '\n\n*****************\n'
	@printf '$(color)Running doctest$(off)\n'
	@printf '*****************\n'
	poetry run coverage run --parallel-mode --source chainmock tests/integrations/i_doctest.py

	@printf '\n\n*****************\n'
	@printf '$(color)Running pytest$(off)\n'
	@printf '*****************\n'
	poetry run coverage run --parallel-mode --source chainmock -m pytest tests/integrations/i_pytest.py

	@printf '\n\n*****************\n'
	@printf '$(color)Running unittest$(off)\n'
	@printf '*****************\n'
	PYTHONPATH=./ poetry run coverage run --parallel-mode --source chainmock tests/integrations/i_unittest.py 2> /dev/null

	@printf '\n\n*****************\n'
	@printf '$(color)Test coverage$(off)\n'
	@printf '*****************\n'
	@poetry run coverage combine --quiet
	poetry run coverage report --fail-under=100 --show-missing

.PHONY: mypy
mypy:
	@printf '\n\n*****************\n'
	@printf '$(color)Running mypy$(off)\n'
	@printf '*****************\n'
	poetry run mypy ${TARGETS}

.PHONY: isort
isort:
	@printf '\n\n*****************\n'
	@printf '$(color)Running isort$(off)\n'
	@printf '*****************\n'
	poetry run isort --check-only ${TARGETS}

.PHONY: black
black:
	@printf '\n\n*****************\n'
	@printf '$(color)Running black$(off)\n'
	@printf '*****************\n'
	poetry run black --check ${TARGETS}

.PHONY: pylint
pylint:
	@printf '\n\n*****************\n'
	@printf '$(color)Running pylint$(off)\n'
	@printf '*****************\n'
	poetry run pylint ${TARGETS}

.PHONY: docs
docs:
	@printf '\n\n*****************\n'
	@printf '$(color)Test building docs$(off)\n'
	@printf '*****************\n'
	poetry run mkdocs build --strict
