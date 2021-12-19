"""Test mocking functionality."""
# pylint: disable=missing-docstring,no-self-use
from typing import Type

import pytest

from mokit._api import MockerState, mocker

from .utils import assert_raises


class SomeClass:
    ATTR = "class_attr"

    def __init__(self) -> None:
        self.attr = "instance_attr"

    def instance_method(self) -> str:
        return self.attr

    def instance_method_with_args(self, arg1: int) -> int:
        return arg1

    @classmethod
    def class_method(cls) -> str:
        return cls.ATTR

    @staticmethod
    def staticmethod() -> str:
        return "static_value"


class TestMocking:
    @pytest.mark.xfail
    def test_pytest_automatic_teardown_when_an_exception_is_raised(self) -> None:
        """Mokit should call teardown even if a test fails with an exception.

        If this does not work, the subsequent tests would fail because mocks are not cleaned up
        properly.
        """
        assert SomeClass().instance_method() == "instance_attr"
        mocker(SomeClass).mock("method").return_value("teardown_mock")
        assert SomeClass().instance_method() == "teardown_mock"
        raise RuntimeError()

    def test_teardown_called(self) -> None:
        assert SomeClass().instance_method() == "instance_attr"

    def test_mock_instance_method_return_value(self) -> None:
        mocker(SomeClass).mock("instance_method").return_value("mocked").called_once()
        assert SomeClass().instance_method() == "mocked"
        MockerState.teardown()
        assert SomeClass().instance_method() == "instance_attr"

    def test_mock_class_method_return_value(self) -> None:
        mocker(SomeClass).mock("class_method").return_value("class_mocked")
        assert SomeClass.class_method() == "class_mocked"
        assert SomeClass().class_method() == "class_mocked"
        MockerState.teardown()
        assert SomeClass.class_method() == "class_attr"
        assert SomeClass().class_method() == "class_attr"

    def test_mock_class_method_on_an_instance(self) -> None:
        instance = SomeClass()
        mocker(instance).mock("class_method").return_value("class_mocked")
        assert instance.class_method() == "class_mocked"
        MockerState.teardown()
        assert instance.class_method() == "class_attr"

    def test_mock_static_method_on_an_instance(self) -> None:
        instance = SomeClass()
        mocker(instance).mock("staticmethod").return_value("static_mocked")
        assert instance.staticmethod() == "static_mocked"
        MockerState.teardown()
        assert instance.staticmethod() == "static_value"

    def test_mock_static_method_return_value(self) -> None:
        mocker(SomeClass).mock("staticmethod").return_value("static_mocked")
        assert SomeClass.staticmethod() == "static_mocked"
        assert SomeClass().staticmethod() == "static_mocked"
        MockerState.teardown()
        assert SomeClass.staticmethod() == "static_value"
        assert SomeClass().staticmethod() == "static_value"

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
            MockerState.teardown()

    def test_mock_called_once_with_no_call(self) -> None:
        mocker(SomeClass).mock("instance_method_with_args").return_value(1).called_once_with(10)
        with assert_raises(
            AssertionError,
            "Expected 'instance_method_with_args' to be called once. Called 0 times.",
        ):
            MockerState.teardown()

    def test_mock_same_method_multiple_times(self) -> None:
        mocker(SomeClass).mock("instance_method").return_value("mocked1")
        assert SomeClass().instance_method() == "mocked1"
        mocker(SomeClass).mock("instance_method").return_value("mocked2")
        assert SomeClass().instance_method() == "mocked2"
        MockerState.teardown()
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

        MockerState.teardown()
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
        MockerState.teardown()

        assert First().get_second().get_third().method() == "value"
