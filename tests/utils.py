"""Utility functions for testing."""
import re
from contextlib import contextmanager
from typing import Generator, Pattern, Type, Union


@contextmanager
def assert_raises(
    expected_exception: Type[BaseException], match: Union[Pattern[str], str]
) -> Generator[None, None, None]:
    """Context manager to assert that an exception is raised with a specific error message.

    Args:
        expected_exception: Exception that is expected to be raised.
        match: String or regex pattern to match the error message against.
    """
    try:
        yield
    except Exception as raised_exception:  # pylint: disable=broad-except
        if not isinstance(raised_exception, expected_exception):
            raise AssertionError(  # pylint: disable=raise-missing-from
                f"Expected exception '{expected_exception}' but '{raised_exception}' was raised"
            )
        fail = False
        if isinstance(match, re.Pattern):
            fail = not match.search(str(raised_exception))
            match = match.pattern
        else:
            fail = str(raised_exception) != str(match)
        if fail:
            raise AssertionError(
                f"Expected error message:\n\n'{str(match)}'\n"
                f"\nBut got:\n\n'{str(raised_exception)}'\n\n"
            ) from raised_exception
    else:
        raise AssertionError(f"Exception '{expected_exception.__name__}' was not raised")
