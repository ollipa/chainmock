"""Test stubbing functionality."""
# pylint: disable=missing-docstring,no-self-use
from mokit._api import mocker


class TestStubbing:
    def test_stubbing(self) -> None:
        stub = mocker().mock("method").return_value("stubbed").self()
        assert stub.method() == "stubbed"  # type: ignore
