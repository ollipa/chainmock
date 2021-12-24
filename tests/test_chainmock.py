"""Test common functionality in Chainmock."""
# pylint: disable=missing-docstring,no-self-use
from chainmock import Assert, Mock, mocker

from .utils import assert_raises


class TestChainmock:
    def test_init_mock_directly_should_fail(self) -> None:
        with assert_raises(
            RuntimeError, "Mock should not be initialized directly. Use mocker function instead."
        ):
            Mock()

    def test_init_assert_directly_should_fail(self) -> None:
        with assert_raises(
            RuntimeError, "Assert should not be initialized directly. Use mocker function instead."
        ):
            mock = mocker()
            Assert(mock, mock._mock, "method")  # pylint: disable=protected-access
