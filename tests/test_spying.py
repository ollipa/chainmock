"""Test spying functionality."""
# pylint: disable=missing-docstring,no-self-use
import pytest

from mokit._api import mocker

from .common import SomeClass
from .utils import assert_raises


class TestMocking:
    @pytest.mark.xfail
    def test_spy_call_count_on_instance_method(self) -> None:
        # TODO: fix spying instance methods
        assert SomeClass().instance_method() == "instance_attr"
        mocker(SomeClass).spy("instance_method").called_once()
        assert SomeClass().instance_method() == "instance_attr"

    def test_spy_call_count_on_class_method(self) -> None:
        assert SomeClass.class_method() == "class_attr"
        mocker(SomeClass).spy("class_method").called_once()
        assert SomeClass.class_method() == "class_attr"

    def test_spy_call_count_on_static_method(self) -> None:
        assert SomeClass.static_method() == "static_value"
        mocker(SomeClass).spy("static_method").called_once()
        assert SomeClass.static_method() == "static_value"

    def test_spying_stub_should_fail(self) -> None:
        with assert_raises(RuntimeError, "Stubs can not be spied. Did you mean to call mock()?"):
            mocker().spy("static_method")
