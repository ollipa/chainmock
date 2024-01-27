"""Test docstring integration and examples in docstrings."""

# pylint: disable=missing-docstring
import asyncio
import doctest
import sys

from chainmock import _api


class SomeClass:
    def method(self) -> str:
        return "some_value"


class Teapot:
    def __init__(self) -> None:
        self._lid = "closed"
        self._state = "empty"

    @property
    def state(self) -> str:
        return self._state

    def brew(self) -> None:
        self._state = "brewing"

    def fill(self) -> None:
        self._state = "full"

    def boil(self) -> None:
        self._state = "boiling"

    def pour(self) -> None:
        self._state = "empty"

    def add_tea(self, tea_type: str, loose: bool = True) -> str:
        if loose:
            return f"loose {tea_type}"
        return f"bagged {tea_type}"

    async def open(self) -> str:
        self._lid = "open"
        return self._lid

    async def close(self) -> str:
        self._lid = "closed"
        return self._lid

    async def timer(self, minutes: int, seconds: int = 0) -> int:
        return minutes + seconds


class TestDoctestTeardown:
    """Test that chainmock cleans up mocks between doctest tests."""

    def test_teardown_doctest_part_1(self) -> None:
        """Part 1. Successful test.

        Examples:
            >>> from chainmock import mocker
            >>> Teapot().add_tea("green")
            'loose green'
            >>> mocker(Teapot).mock("add_tea").return_value("mocked1").called_once()
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("green")
            'mocked1'
        """

    def test_teardown_doctest_part_2(self) -> None:
        """Part 2. Verify that Teapot is not mocked anymore.

        Examples:
            >>> Teapot().add_tea("black")
            'loose black'
        """


if __name__ == "__main__":
    results1 = doctest.testmod(
        sys.modules[__name__],  # current module
        extraglobs={"Teapot": Teapot},
        optionflags=doctest.ELLIPSIS,
    )
    results2 = doctest.testmod(
        _api,
        extraglobs={
            "Teapot": Teapot,
            "teapot": Teapot(),
            "asyncio": asyncio,
        },
        optionflags=doctest.ELLIPSIS,
    )
    test_count = results1.attempted + results2.attempted
    failed_count = results1.failed + results2.failed
    if results1.failed or results2.failed:
        print(f"Doctests FAILED (tests={test_count}, failed={failed_count})\n")
        sys.exit(1)
    print(f"Doctests successful (tests={test_count}, failed={failed_count})\n")
    sys.exit(0)
