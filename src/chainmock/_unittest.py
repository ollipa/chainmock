"""Chainmock unittest integration."""

import functools
import sys
import unittest

from ._api import State

original_stop_test = unittest.TestResult.stopTest


@functools.wraps(original_stop_test)
def new_stop_test(self: unittest.TestResult, test: unittest.TestCase) -> None:
    """Run chainmock teardown between unittest tests."""
    State.reset_mocks()
    if self.failures and self.failures[-1][0] is test:
        # Test already failed, do not validate mocks
        State.reset_state()
        return original_stop_test(self, test)
    if self.errors and self.errors[-1][0] is test:
        # Test already errored, do not validate mocks
        State.reset_state()
        return original_stop_test(self, test)

    try:
        State.validate_mocks()
    except BaseException:  # pylint: disable=broad-except
        self.addFailure(test, sys.exc_info())
    return original_stop_test(self, test)


unittest.TestResult.stopTest = new_stop_test  # type: ignore
