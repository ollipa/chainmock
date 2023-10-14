"""Test pytest integration."""
from typing import Any

from tests import DefaultTestCase


class TestPytest(DefaultTestCase):
    """Tests for unittest integration."""


def test_teardown_on_chainmock_success(testdir: Any) -> None:
    """Test that mocks are teared down after a successful test."""
    testdir.makepyfile(
        """
        from chainmock import mocker

        class FooClass:

            def method(self):
                return "value"

        def test_teardown_part1():
            assert FooClass().method() == "value"
            mocker(FooClass).mock("method").return_value("mocked").called_once()
            assert FooClass().method() == "mocked"

        def test_teardown_part2():
            assert FooClass().method() == "value"
        """
    )
    result = testdir.runpytest("-p", "no:asyncio")
    result.assert_outcomes(passed=2)


def test_teardown_on_chainmock_failure(testdir: Any) -> None:
    """Test that mocks are teared down after chainmock validations fail."""
    testdir.makepyfile(
        """
        from chainmock import mocker

        class FooClass:

            def method(self):
                return "value"

        def test_teardown_part1():
            assert FooClass().method() == "value"
            mocker(FooClass).mock("method").return_value("mocked").called_twice()
            assert FooClass().method() == "mocked"

        def test_teardown_part2():
            assert FooClass().method() == "value"
        """
    )
    result = testdir.runpytest("-p", "no:asyncio")
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.re_match_lines(
        [r".+AssertionError: Expected 'FooClass.method' to have been called twice. Called once."]
    )


def test_teardown_on_other_failure(testdir: Any) -> None:
    """Test that mocks are teared down after test failure not related to chainmock.

    Chainmock validators should not be executed if test fails before validators are executed.
    """
    testdir.makepyfile(
        """
        from chainmock import mocker

        class FooClass:

            def method(self):
                return "value"

        def test_teardown():
            assert FooClass().method() == "value"
            mocker(FooClass).mock("method").return_value("mocked")
            assert FooClass().method() == "mocked"
            assert True is False

        def test_teardown_part2():
            assert FooClass().method() == "value"
        """
    )
    result = testdir.runpytest("-p", "no:asyncio")
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.no_re_match_line(r".+AssertionError: Expected 'FooClass.method'")


def test_teardown_on_fixture_failure(testdir: Any) -> None:
    """Test that mocks are teared down after a test fails before test case is
    executed.
    """
    testdir.makepyfile(
        """
        import pytest

        from chainmock import mocker

        class FooClass:

            def method(self):
                return "value"

        class TestClass1:

            @pytest.fixture(autouse=True)
            def mock_fooclass(self):
                mocked = mocker(FooClass).mock("method").return_value("mocked").called_twice()

            @pytest.fixture()
            def invalid_fixture(self):
                return {
                    {
                        "foo": "bar"
                    }
                }

            def test_teardown(self, invalid_fixture):
                assert FooClass().method() == "mocked"
                assert FooClass().method() == "mocked"

        class TestClass2:

            def test_teardown(self):
                assert FooClass().method() == "value"
        """
    )
    result = testdir.runpytest("-p", "no:asyncio")
    result.assert_outcomes(passed=1, errors=1)
    result.stdout.re_match_lines(r".+TypeError: unhashable type: 'dict'")
