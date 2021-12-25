"""Pytest plugin."""
from typing import Generator, Optional

import pytest
from _pytest.runner import CallInfo, ExceptionInfo, Item, TestReport

from ._api import State


@pytest.hookimpl(hookwrapper=True)  # type: ignore
def pytest_runtest_makereport(
    item: Item,  # pylint: disable=unused-argument
    call: CallInfo[None],
) -> Generator[None, None, None]:
    """Hook into test execution and execute teardown after a test."""
    if call.when == "call":
        State.reset_mocks()
        if call.excinfo is None:
            try:
                State.validate_mocks()
            except BaseException:  # pylint: disable=broad-except
                call.excinfo = ExceptionInfo.from_current()
        else:
            # Reset state without running validations so that validations
            # do not leak to the next test.
            State.reset_state()

    _test_report: Optional[TestReport] = yield
