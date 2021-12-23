
color := $(shell tput setaf 2)
off := $(shell tput sgr0)
TARGETS = src tests

.PHONY: all
all: lint test

.PHONY: lint
lint: isort black mypy pylint

.PHONY: test
test: install pytest

.PHONY: install
install:
	@printf '\n\n*****************\n'
	@printf '$(color)Installing package$(off)\n'
	@printf '*****************\n'
ifeq (${VIRTUAL_ENV},)
	@printf 'Skipping install. VIRTUAL_ENV is not set.\n'
else
	pip install .
endif

.PHONY: pytest
pytest:
	@printf '\n\n*****************\n'
	@printf '$(color)Running pytest$(off)\n'
	@printf '*****************\n'
	pytest tests

.PHONY: mypy
mypy:
	@printf '\n\n*****************\n'
	@printf '$(color)Running mypy$(off)\n'
	@printf '*****************\n'
	mypy ${TARGETS}

.PHONY: isort
isort:
	@printf '\n\n*****************\n'
	@printf '$(color)Running isort$(off)\n'
	@printf '*****************\n'
	isort --check-only ${TARGETS}

.PHONY: black
black:
	@printf '\n\n*****************\n'
	@printf '$(color)Running black$(off)\n'
	@printf '*****************\n'
	black --check ${TARGETS}

.PHONY: pylint
pylint:
	@printf '\n\n*****************\n'
	@printf '$(color)Running pylint$(off)\n'
	@printf '*****************\n'
	pylint ${TARGETS}

.PHONY: coverage
coverage:
	@printf '\n\n*****************\n'
	@printf '$(color)Running coverage$(off)\n'
	@printf '*****************\n'
	coverage run --source chainmock -m pytest tests
	coverage report --fail-under=100 --show-missing