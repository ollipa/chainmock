"""Test unittest integration."""

# pylint: disable=missing-docstring
import sys
import unittest

from chainmock import mocker
from tests import DefaultTestCase


class FooClass:
    def method(self) -> str:
        return "value"


class TestUnitTestIntegration(DefaultTestCase, unittest.IsolatedAsyncioTestCase):
    """Tests for unittest integration."""


class TestTeardownOnSuccess(unittest.TestCase):
    """Test that mocks are teared down after a successful test."""

    def test_this_test_is_succesful(self) -> None:
        self.assertEqual(FooClass().method(), "value")
        mocker(FooClass).mock("method").return_value("mocked").called_once()
        self.assertEqual(FooClass().method(), "mocked")

    def test_teardown_after_success(self) -> None:
        self.assertEqual(FooClass().method(), "value")


class TestTeardownOnValidationFailure(unittest.TestCase):
    """Test that mocks are teared down after chainmock validations fail."""

    def test_this_test_should_fail(self) -> None:
        self.assertEqual(FooClass().method(), "value")
        mocker(FooClass).mock("method").return_value("mocked").called_twice()
        self.assertEqual(FooClass().method(), "mocked")

    def test_teardown_after_validation_failure(self) -> None:
        self.assertEqual(FooClass().method(), "value")


class TestTeardownOnRunnerFailure(unittest.TestCase):
    """Test that mocks are teared down after test failure not related to chainmock."""

    def test_this_test_should_fail(self) -> None:
        self.assertEqual(FooClass().method(), "value")
        mocker(FooClass).mock("method").return_value("mocked")
        self.assertEqual(FooClass().method(), "mocked")
        self.assertEqual("this test should fail", "ok")

    def test_teardown_after_runner_failure(self) -> None:
        self.assertEqual(FooClass().method(), "value")


class TestNoDuplicatedFailures(unittest.TestCase):
    """Test that failures are not added twice if test fails before chainmock teardown.

    Expected failure count should have too high value if there are too many failures.
    """

    def test_this_test_should_fail(self) -> None:
        self.assertEqual(FooClass().method(), "value")
        mocker(FooClass).mock("method").return_value("mocked").called_twice()
        self.assertEqual(FooClass().method(), "mocked")
        self.assertEqual("this test should fail", "ok")


class TestNoFailureOnError(unittest.TestCase):
    """Test that chainmock does not add test failure if an error is already
    reported for the test.
    """

    def test_this_test_should_error(self) -> None:
        self.assertEqual(FooClass().method(), "value")
        mocker(FooClass).mock("method").return_value("mocked").called_twice()
        self.assertEqual(FooClass().method(), "mocked")
        raise RuntimeError("this test should error")

    def test_teardown_after_runner_error(self) -> None:
        self.assertEqual(FooClass().method(), "value")


def run_tests() -> None:
    expected_failures = 3
    expected_errors = 1
    test = unittest.main(exit=False)

    test_count = test.result.testsRun
    error_count = len(test.result.errors)
    failed_count = len(test.result.failures)

    print(f"Expected failures {expected_failures}, errors {expected_errors}\n")
    print(
        f"Tests={test_count}, "
        f"Failed={failed_count}/{expected_failures}, "
        f"Errors={error_count}/{expected_errors}"
    )

    if test_count < 250 or failed_count != expected_failures or error_count != expected_errors:
        print("Unittest test run FAILED\n")
        sys.exit(1)

    print("Unittest test run SUCCESSFUL\n")
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
