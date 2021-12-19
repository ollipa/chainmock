"""Test spying functionality."""
# pylint: disable=missing-docstring,no-self-use
from mokit._api import mocker

from .common import SomeClass
from .utils import assert_raises


class TestMocking:
    def test_spy_call_count(self) -> None:
        assert SomeClass.staticmethod() == "static_value"
        mocker(SomeClass).spy("staticmethod").called_once()
        assert SomeClass.staticmethod() == "static_value"

    def test_spying_stub_should_fail(self) -> None:
        with assert_raises(RuntimeError, "Stubs can not be spied. Did you mean to call mock()?"):
            mocker().spy("staticmethod")
