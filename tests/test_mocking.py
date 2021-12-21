"""Test mocking functionality."""
# pylint: disable=missing-docstring,no-self-use
from typing import Type

import pytest

from chainmock import mocker
from chainmock._api import State
from chainmock.mock import call

from . import common
from .common import DerivedClass, SomeClass
from .utils import assert_raises


class TestMocking:
    @pytest.mark.xfail
    def test_pytest_automatic_teardown_when_an_exception_is_raised(self) -> None:
        """Teardown should be called even if a test fails with an exception.

        If this does not work, the subsequent tests would fail because mocks are not cleaned up
        properly.
        """
        assert SomeClass().instance_method() == "instance_attr"
        mocker(SomeClass).mock("instance_method").return_value("teardown_mock")
        assert SomeClass().instance_method() == "teardown_mock"
        raise RuntimeError()

    def test_teardown_called(self) -> None:
        assert SomeClass().instance_method() == "instance_attr"

    def test_mock_module_function_return_value(self) -> None:
        mocker(common).mock("some_function").return_value("mocked").called_once()
        assert common.some_function("foo") == "mocked"
        State.teardown()
        assert common.some_function("foo") == "foo"

    def test_mock_instance_method_return_value(self) -> None:
        mocker(SomeClass).mock("instance_method").return_value("mocked").called_once()
        assert SomeClass().instance_method() == "mocked"
        State.teardown()
        assert SomeClass().instance_method() == "instance_attr"

    def test_mock_class_method_return_value(self) -> None:
        mocker(SomeClass).mock("class_method").return_value("class_mocked")
        assert SomeClass.class_method() == "class_mocked"
        assert SomeClass().class_method() == "class_mocked"
        State.teardown()
        assert SomeClass.class_method() == "class_attr"
        assert SomeClass().class_method() == "class_attr"

    def test_mock_property_return_value(self) -> None:
        mocker(SomeClass).mock("some_property").return_value("propertymocked")
        assert SomeClass().some_property == "propertymocked"
        State.teardown()
        assert SomeClass().some_property == "instance_attr"

    def test_mock_and_set_properties_with_kwargs(self) -> None:
        mocker(SomeClass, some_property="foo", instance_method="bar")
        assert SomeClass().some_property == "foo"
        assert SomeClass().instance_method() == "bar"
        State.teardown()
        assert SomeClass().some_property == "instance_attr"
        assert SomeClass().instance_method() == "instance_attr"

    def test_mock_class_method_on_an_instance(self) -> None:
        instance = SomeClass()
        mocker(instance).mock("class_method").return_value("class_mocked")
        assert instance.class_method() == "class_mocked"
        State.teardown()
        assert instance.class_method() == "class_attr"

    def test_mock_static_method_on_an_instance(self) -> None:
        instance = SomeClass()
        mocker(instance).mock("static_method").return_value("static_mocked")
        assert instance.static_method() == "static_mocked"
        State.teardown()
        assert instance.static_method() == "static_value"

    def test_mock_static_method_return_value(self) -> None:
        mocker(SomeClass).mock("static_method").return_value("static_mocked")
        assert SomeClass.static_method() == "static_mocked"
        assert SomeClass().static_method() == "static_mocked"
        State.teardown()
        assert SomeClass.static_method() == "static_value"
        assert SomeClass().static_method() == "static_value"

    def test_mock_side_effect_raise_exception(self) -> None:
        mocker(SomeClass).mock("instance_method").side_effect(RuntimeError("error")).called_once()
        with assert_raises(RuntimeError, "error"):
            SomeClass().instance_method()

    def test_mock_side_effect_multiple_return_values(self) -> None:
        mocker(SomeClass).mock("instance_method").side_effect(["1", "2", "3"]).called_times(3)
        assert SomeClass().instance_method() == "1"
        assert SomeClass().instance_method() == "2"
        assert SomeClass().instance_method() == "3"

    def test_mock_called_once_with(self) -> None:
        mocker(SomeClass).mock("instance_method_with_args").return_value(1).called_once_with(10)
        assert SomeClass().instance_method_with_args(10) == 1

    def test_mock_called_once_with_wrong_arg(self) -> None:
        mocker(SomeClass).mock("instance_method_with_args").return_value(1).called_once_with(10)
        SomeClass().instance_method_with_args(5)
        with assert_raises(
            AssertionError,
            (
                "expected call not found.\n"
                "Expected: instance_method_with_args(10)\n"
                "Actual: instance_method_with_args(5)"
            ),
        ):
            State.teardown()

    def test_mock_called_once_with_no_call(self) -> None:
        mocker(SomeClass).mock("instance_method_with_args").return_value(1).called_once_with(10)
        with assert_raises(
            AssertionError,
            "Expected 'instance_method_with_args' to be called once. Called 0 times.",
        ):
            State.teardown()

    def test_mock_same_method_multiple_times(self) -> None:
        mocker(SomeClass).mock("instance_method").return_value("mocked1")
        assert SomeClass().instance_method() == "mocked1"
        mocker(SomeClass).mock("instance_method").return_value("mocked2")
        assert SomeClass().instance_method() == "mocked2"
        State.teardown()
        assert SomeClass().instance_method() == "instance_attr"

    def test_mock_class_and_instance_at_the_same_time(self) -> None:
        class FooClass:
            def method(self) -> str:
                return "value"

        mocker(FooClass).mock("method").return_value("mocked1")
        assert FooClass().method() == "mocked1"

        instance = FooClass()
        mocker(instance).mock("method").return_value("mocked2")
        assert FooClass().method() == "mocked1"
        assert instance.method() == "mocked2"

        State.teardown()
        assert FooClass().method() == "value"
        assert instance.method() == "value"

    def test_mock_chaining_methods(self) -> None:
        class Third:
            @classmethod
            def method(cls) -> str:
                return "value"

        class Second:
            def get_third(self) -> Type[Third]:
                return Third

        class First:
            def get_second(self) -> Second:
                return Second()

        assert First().get_second().get_third().method() == "value"

        mocker(First).mock("get_second.get_third.method").return_value("mock_chain")
        assert First().get_second().get_third().method() == "mock_chain"
        State.teardown()

        assert First().get_second().get_third().method() == "value"

    def test_mock_instance_method_on_derived_class(self) -> None:
        mocker(DerivedClass).mock("instance_method").return_value("foo").called_once()
        assert DerivedClass().instance_method() == "foo"
        State.teardown()
        assert DerivedClass().instance_method() == "instance_attr"

    def test_mock_instance_method_on_derived_class_and_base_class(self) -> None:
        mocker(SomeClass).mock("instance_method").return_value("foo").called_once()
        assert SomeClass().instance_method() == "foo"
        mocker(DerivedClass).mock("instance_method").return_value("bar").called_once()
        assert DerivedClass().instance_method() == "bar"
        State.teardown()
        assert SomeClass().instance_method() == "instance_attr"
        assert DerivedClass().instance_method() == "instance_attr"

    def test_mock_class_method_on_derived_class(self) -> None:
        mocker(DerivedClass).mock("class_method").return_value("foo").called_twice()
        assert DerivedClass().class_method() == "foo"
        assert DerivedClass.class_method() == "foo"
        State.teardown()
        assert DerivedClass().class_method() == "class_attr"
        assert DerivedClass.class_method() == "class_attr"

    def test_mock_class_method_on_derived_class_and_base_class(self) -> None:
        mocker(SomeClass).mock("class_method").return_value("foo").called_once()
        assert SomeClass.class_method() == "foo"
        mocker(DerivedClass).mock("class_method").return_value("bar").called_twice()
        assert DerivedClass().class_method() == "bar"
        assert DerivedClass.class_method() == "bar"
        State.teardown()
        assert SomeClass.class_method() == "class_attr"
        assert DerivedClass().class_method() == "class_attr"
        assert DerivedClass.class_method() == "class_attr"

    def test_mock_static_method_on_derived_class(self) -> None:
        mocker(DerivedClass).mock("static_method").return_value("foo").called_twice()
        assert DerivedClass().static_method() == "foo"
        assert DerivedClass.static_method() == "foo"
        State.teardown()
        assert DerivedClass().static_method() == "static_value"
        assert DerivedClass.static_method() == "static_value"

    def test_mock_static_method_on_derived_class_and_base_class(self) -> None:
        mocker(SomeClass).mock("static_method").return_value("foo").called_once()
        assert SomeClass.static_method() == "foo"
        mocker(DerivedClass).mock("static_method").return_value("bar").called_twice()
        assert DerivedClass().static_method() == "bar"
        assert DerivedClass.static_method() == "bar"
        State.teardown()
        assert SomeClass.static_method() == "static_value"
        assert DerivedClass().static_method() == "static_value"
        assert DerivedClass.static_method() == "static_value"

    def test_mock_instance_method_on_derived_class_called_with_args(self) -> None:
        mocker(DerivedClass).mock("instance_method_with_args").called_with(1).return_value(
            2
        ).called_once()
        assert DerivedClass().instance_method_with_args(1) == 2

    def test_mock_instance_method_on_derived_class_and_base_class_called_with_args(self) -> None:
        mocker(SomeClass).mock("instance_method_with_args").called_with(1).return_value(
            2
        ).called_once()
        assert SomeClass().instance_method_with_args(1) == 2
        mocker(DerivedClass).mock("instance_method_with_args").called_with(2).return_value(
            3
        ).called_once()
        assert DerivedClass().instance_method_with_args(2) == 3

    def test_mock_class_method_on_derived_class_called_with_args(self) -> None:
        mocker(DerivedClass).mock("class_method_with_args").has_calls(
            [call(1), call(1)]
        ).return_value(2).called_twice()
        assert DerivedClass().class_method_with_args(1) == 2
        assert DerivedClass.class_method_with_args(1) == 2

    def test_mock_class_method_on_derived_class_and_base_class_called_with_args(self) -> None:
        mocker(SomeClass).mock("class_method_with_args").called_with(1).return_value(
            2
        ).called_once()
        assert SomeClass.class_method_with_args(1) == 2
        mocker(DerivedClass).mock("class_method_with_args").has_calls(
            [call(2), call(2)]
        ).return_value(3).called_twice()
        assert DerivedClass().class_method_with_args(2) == 3
        assert DerivedClass.class_method_with_args(2) == 3

    def test_mock_static_method_on_derived_class_called_with_args(self) -> None:
        mocker(DerivedClass).mock("static_method_with_args").has_calls(
            [call(1), call(1)]
        ).return_value(2).called_twice()
        assert DerivedClass().static_method_with_args(1) == 2
        assert DerivedClass.static_method_with_args(1) == 2

    def test_mock_static_method_on_derived_class_and_base_class_called_with_args(self) -> None:
        mocker(SomeClass).mock("static_method_with_args").called_with(1).return_value(
            2
        ).called_once()
        assert SomeClass.static_method_with_args(1) == 2
        mocker(DerivedClass).mock("static_method_with_args").has_calls(
            [call(2), call(2)]
        ).return_value(3).called_twice()
        assert DerivedClass().static_method_with_args(2) == 3
        assert DerivedClass.static_method_with_args(2) == 3
