"""Test pytest plugin."""
from typing import Any


# Pytester available only in Pytest>=6.2
# testdir: Pytest.Pytester
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
    """Test that mocks are teared down after a chainmock validations fail."""
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
