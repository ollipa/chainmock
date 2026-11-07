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
- [Releasing a new version](#releasing-a-new-version)
- [License](#license)

## How can I contribute?

### Reporting bugs

If you discover a bug, please [create an issue](https://github.com/ollipa/chainmock/issues/new/choose) and include as much detail as possible. Describe the issue, steps to reproduce, and the expected and actual behavior.

### Suggesting enhancements

If you have an idea for an enhancement or new feature, please create an issue on GitHub to discuss it. Provide a clear and concise description of the proposed feature and its use case.

### Contributing code

We welcome code contributions! If you would like to contribute code, please follow the instructions below.

## Getting started

Before you start contributing, ensure that you have the latest version of `uv` installed. See [uv documentation](https://docs.astral.sh/uv/) for installation instructions.

After installing `uv`, run the following command to install the project's dependencies:

```bash
uv venv
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

Tox is used to run tests in multiple Python environments. To execute tests with different Python versions you need to first have the Python versions installed locally. You can use [uv](https://docs.astral.sh/uv/guides/install-python/) to install multiple Python versions:

```
uv python install 3.13 3.14
```

After installing the Python versions, you can run the tests with the following command:

```bash
tox
```

The above command will run all the tests in all the Python versions defined in `tox.ini` file. You can also run the tests in a specific Python version with the `-e` flag:

```bash
tox -e py314
```

For more information see the [Tox documentation](https://tox.wiki/).

## Updating documentation

The documentation is created using [Mkdocs](https://www.mkdocs.org/). To test the documentation locally, run the following command:

```bash
mkdocs serve
```

For more details see the [Mkdocs documentation](https://www.mkdocs.org/user-guide/) and [Material for Mkdocs documentation](https://squidfunk.github.io/mkdocs-material/).

The documentation is hosted in [Read the Docs](https://about.readthedocs.com/) and is automatically built and deployed when a pull request is merged.

## Releasing a new version

Releases are made with `scripts/release.py`. It needs [GitHub CLI](https://cli.github.com/)
and a clean `main` branch that is in sync with `origin/main`.

1. Bump the version, push it to `main` and create the GitHub release. Choose `major`,
   `minor` or `patch` following semantic versioning:

   ```bash
   uv run scripts/release.py bump minor
   ```

   The script updates the version in `pyproject.toml` and `uv.lock` and moves the
   entries in the `Unreleased` section of `CHANGELOG.md` under the new version. It shows
   the changes and asks for confirmation before it commits them and pushes the commit
   directly to `main`. It then shows the release notes and asks for confirmation before
   it creates the GitHub release and its `v`-prefixed tag at the pushed commit.

   If you decline creating the release, or it fails, create it later from an up-to-date
   `main` with `uv run scripts/release.py release`.

2. The release starts the publish workflow, which first runs the CI workflow. After the
   tests and linters pass and the release checks succeed, the workflow waits for
   approval to deploy to the `pypi` environment. Before approving, check that the commit
   of the run is on `main` and that its `.github/workflows/` directory is the same as on
   `main`.

Saving a draft or publishing a pre-release does not publish anything to PyPI, but
changing a pre-release to a release does start the workflow.

If the workflow fails before the deployment, nothing has been uploaded to PyPI. Fix the
problem on `main`, remove the failed release with `gh release delete v1.2.3 --cleanup-tag`
and create it again. If the fix changes the released code, bump a new version instead.

### Release infrastructure

PyPI trusted publishing is tied to the workflow file `publish.yml` and the `pypi`
environment. The manual approval exists only if the `pypi` environment has required
reviewers: GitHub creates a missing environment without any protection when a workflow
references it. Do not delete or rename the environment, and do not leave the environment
name blank in the PyPI trusted publisher.

## License

By contributing to this project, you agree to the [License](https://github.com/ollipa/chainmock/blob/main/LICENSE) of this repository.

Thank you for your contributions!
