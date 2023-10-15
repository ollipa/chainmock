# Contributing to Chainmock

We appreciate your interest in contributing to our open-source project. Please take a moment to review the following instructions to make sure everything goes smoothly.

## Table of Contents

- [How can I contribute?](#how-can-i-contribute)
  - [Reporting bugs](#reporting-bugs)
  - [Suggesting enhancements](#suggesting-enhancements)
  - [Contributing code](#contributing-code)
- [Getting started](#getting-started)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Testing and linters](#testing-and-linters)
- [Running tests with Tox](#running-tests-with-tox)
- [Updating documentation](#updating-documentation)
- [License](#license)

## How can I contribute?

### Reporting bugs

If you discover a bug, please [create an issue](https://github.com/ollipa/chainmock/issues/new/choose) and include as much detail as possible. Describe the issue, steps to reproduce, and the expected and actual behavior.

### Suggesting enhancements

If you have an idea for an enhancement or new feature, please create an issue on GitHub to discuss it. Provide a clear and concise description of the proposed feature and its use case.

### Contributing code

We welcome code contributions! If you would like to contribute code, please follow the instructions below.

## Getting started

Before you start contributing, ensure that you have the latest version of Poetry installed. See [Poetry documentation](https://python-poetry.org/docs/#installation) for installation instructions.

After installing Poetry, run the following command to install the project's dependencies:

```bash
poetry install
```

After installing the dependencies, run the following command to activate the project's virtual environment:

```bash
poetry shell
```

## Pull Request Guidelines

Please follow these guidelines when submitting a pull request:

- Update documentation related to your changes if applicable.
- Include tests for your changes if applicable.
- Ensure that your pull request has a clear title and description.
- Reference any related issues in the description.

## Testing and linters

Tests and linters are automatically run on every pull request. You can run them locally with the following Makefile commands:

```bash
# Run tests and linters
make
# Run only linters
make lint
# Run only tests
make test
```

## Running tests with Tox

Tox is used to run tests in multiple Python environments. To execute tests with different Python versions you need to first have the Python versions installed locally. You can use, for example, [pyenv](https://github.com/pyenv/pyenv) project to install multiple Python versions.

After installing the Python versions, you can run the tests with the following command:

```bash
tox
```

The above command will run all the tests in all the Python versions defined in `tox.ini` file. You can also run the tests in a specific Python version with the `-e` flag:

```bash
tox -e py312
```

For more information see the [Tox documentation](https://tox.wiki/).

## Updating documentation

The documentation is created using [Mkdocs](https://www.mkdocs.org/). To test the documentation locally, run the following command:

```bash
mkdocs serve
```

For more details see the [Mkdocs documentation](https://www.mkdocs.org/user-guide/) and [Material for Mkdocs documentation](https://squidfunk.github.io/mkdocs-material/).

The documentation is hosted in [Read the Docs](https://about.readthedocs.com/) and is automatically built and deployed when a pull request is merged. Documentation dependencies that Read the Docs installs are defined in `docs/requirements.txt`. To regenerate the dependency file, run the following command:

```bash
make docs-requirements
```

## License

By contributing to this project, you agree to the [License](LICENSE) of this repository.

Thank you for your contributions!
