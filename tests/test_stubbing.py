"""Test stubbing functionality."""
# pylint: disable=missing-docstring,no-self-use
from chainmock import mocker

from .utils import assert_raises


class TestStubbing:
    def test_stubbing(self) -> None:
        stub = mocker().mock("method").return_value("stubbed").self()
        assert stub.method() == "stubbed"  # type: ignore

    def test_stubbing_internal_attribute(self) -> None:
        with assert_raises(ValueError, "Cannot replace Mock internal attribute _reset"):
            mocker().mock("_reset").return_value("stubbed").self()

    def test_stub_chaining(self) -> None:
        stub = mocker().mock("method.another_method").return_value("stubbed").self()
        assert stub.method().another_method() == "stubbed"  # type: ignore
