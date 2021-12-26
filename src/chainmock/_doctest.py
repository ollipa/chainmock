"""Chainmock doctest integration."""
import functools
from doctest import DocTestRunner, TestResults
from typing import Any

from ._api import State

original_run = DocTestRunner.run


@functools.wraps(original_run)
def new_run(
    *args: Any,
    **kwargs: Any,
) -> TestResults:
    """Run chainmock teardown between doctest tests."""
    try:
        return original_run(*args, **kwargs)
    finally:
        State.teardown()


DocTestRunner.run = new_run  # type: ignore
