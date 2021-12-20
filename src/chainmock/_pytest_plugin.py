"""Pytest plugin."""
from typing import Generator

import pytest
from pytest import Item

from ._api import State


@pytest.hookimpl(hookwrapper=True)  # type: ignore
def pytest_runtest_call(
    item: Item,  # pylint: disable=unused-argument
) -> Generator[None, None, None]:
    """Hook into test execution and execute teardown after a test."""
    try:
        yield
    finally:
        State.reset_mocks()
    State.teardown()
