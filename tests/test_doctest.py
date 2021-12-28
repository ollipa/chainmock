"""Test examples in docstrings."""
# pylint: disable=missing-docstring,no-self-use
import asyncio
import doctest
import sys

from chainmock import _api


class Teapot:
    def brew(self) -> None:
        pass

    def fill(self) -> None:
        pass

    def boil(self) -> None:
        pass

    def pour(self) -> None:
        pass

    def add_tea(self, tea_type: str, loose: bool = True) -> str:
        if loose:
            return f"loose {tea_type}"
        return f"bagged {tea_type}"

    async def open(self) -> None:
        pass

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
        extraglobs={"Teapot": Teapot, "teapot": Teapot(), "asyncio": asyncio},
        optionflags=doctest.ELLIPSIS,
    )
    if results1.failed or results2.failed:
        print("Doctests FAILED")
        sys.exit(1)
    print("Doctests successful")
    sys.exit(0)
