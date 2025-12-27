"""Test mocking functionality."""

# pylint: disable=missing-docstring,too-many-lines
import builtins
import re
import sys
from typing import Any

from chainmock import mocker
from chainmock._api import State
from chainmock.mock import ANY_INT, ANY_STR, call

from . import common
from .common import DerivedClass, Proxy, SomeClass
from .utils import assert_raises


class MockingTestCase:
    def test_mock_should_cache_asserts(self) -> None:
        assert1 = mocker(SomeClass).mock("instance_method")
        assert2 = mocker(SomeClass).mock("instance_method")
        assert assert1 is assert2

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

    def test_mock_property_call_count(self) -> None:
        mocker(SomeClass).mock("some_property").called_once().return_value("propertymocked")
        assert SomeClass().some_property == "propertymocked"

    def test_mock_property_call_count_fail(self) -> None:
        mocker(SomeClass).mock("some_property").called_twice().return_value("propertymocked")
        assert SomeClass().some_property == "propertymocked"
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.some_property' to have been called twice. "
            "Called once.\nCalls: [call()].",
        ):
            State.teardown()

    def test_mock_force_property(self) -> None:
        mocker(SomeClass).mock("instance_method", force_property=True).called_once().return_value(
            "mocked"
        )
        # pylint: disable=comparison-with-callable
        assert SomeClass().instance_method == "mocked"  # type: ignore

    def test_mock_create_unknown_property(self) -> None:
        mocker(SomeClass).mock("unknown_property", force_property=True, create=True).return_value(
            "mocked"
        )
        # pylint: disable=no-member
        assert SomeClass().unknown_property == "mocked"  # type: ignore
        assert hasattr(SomeClass, "unknown_property")
        State.teardown()
        assert not hasattr(SomeClass, "unknown_property")

    def test_mock_and_set_properties_with_kwargs(self) -> None:
        mocker(SomeClass, some_property="foo", instance_method=lambda: "bar")
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
        mocker(SomeClass).mock("instance_method").side_effect(["1", "2", "3"]).call_count(3)
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
            re.compile(
                r"expected call not found.\n"
                r"Expected: SomeClass.instance_method_with_args\(10\)\n"
                r"\s*Actual: SomeClass.instance_method_with_args\(5\)"
            ),
        ):
            State.teardown()

    def test_mock_called_once_with_no_call(self) -> None:
        mocker(SomeClass).mock("instance_method_with_args").return_value(1).called_once_with(10)
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.instance_method_with_args' to be called once. Called 0 times.",
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

    def test_mock_chained_methods(self) -> None:
        class Third:
            @classmethod
            def method(cls) -> str:
                return "value"

        class Second:
            def get_third(self) -> type[Third]:
                return Third

        class First:
            def get_second(self) -> Second:
                return Second()

        assert First().get_second().get_third().method() == "value"

        mocker(First).mock("get_second.get_third.method").return_value("mock_chain")
        assert First().get_second().get_third().method() == "mock_chain"
        State.teardown()
        assert First().get_second().get_third().method() == "value"

    def test_mock_chained_property(self) -> None:
        class Second:
            @property
            def prop(self) -> str:
                return "value"

        class First:
            def get_prop(self) -> Second:
                return Second()

        assert First().get_prop().prop == "value"

        mocker(First).mock("get_prop.prop", force_property=True).return_value("mock_prop")
        assert First().get_prop().prop == "mock_prop"
        State.teardown()
        assert First().get_prop().prop == "value"

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
        mocker(DerivedClass).mock("instance_method_with_args").called_last_with(1).return_value(
            2
        ).called_once()
        assert DerivedClass().instance_method_with_args(1) == 2

    def test_mock_instance_method_on_derived_class_and_base_class_called_with_args(
        self,
    ) -> None:
        mocker(SomeClass).mock("instance_method_with_args").called_last_with(1).return_value(
            2
        ).called_once()
        assert SomeClass().instance_method_with_args(1) == 2
        mocker(DerivedClass).mock("instance_method_with_args").called_last_with(2).return_value(
            3
        ).called_once()
        assert DerivedClass().instance_method_with_args(2) == 3

    def test_mock_class_method_on_derived_class_called_with_args(self) -> None:
        mocker(DerivedClass).mock("class_method_with_args").has_calls(
            [call(1), call(1)]
        ).return_value(2).called_twice()
        assert DerivedClass().class_method_with_args(1) == 2
        assert DerivedClass.class_method_with_args(1) == 2

    def test_mock_class_method_on_derived_class_and_base_class_called_with_args(
        self,
    ) -> None:
        mocker(SomeClass).mock("class_method_with_args").called_last_with(1).return_value(
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

    def test_mock_static_method_on_derived_class_and_base_class_called_with_args(
        self,
    ) -> None:
        mocker(SomeClass).mock("static_method_with_args").called_last_with(1).return_value(
            2
        ).called_once()
        assert SomeClass.static_method_with_args(1) == 2
        mocker(DerivedClass).mock("static_method_with_args").has_calls(
            [call(2), call(2)]
        ).return_value(3).called_twice()
        assert DerivedClass().static_method_with_args(2) == 3
        assert DerivedClass.static_method_with_args(2) == 3

    def test_mock_instance_method_called_last_with(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").called_last_with("foo", arg2=5)
        FooClass().method("foo", arg2=5)
        State.teardown()

        mocker(FooClass).mock("method").called_last_with(ANY_STR, arg2=ANY_INT)
        FooClass().method("bar", arg2=42)
        State.teardown()

        mocker(FooClass).mock("method").called_last_with("foo", arg2=5)
        FooClass().method("foo", arg2=10)
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: FooClass.method\('foo', arg2=5\)\n"
                r"\s*Actual: FooClass.method\('foo', arg2=10\)"
            ),
        ):
            State.teardown()

    def test_mock_instance_method_any_call_with(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").any_call_with("bar", arg2=2)
        FooClass().method("foo", arg2=1)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").any_call_with("foo", arg2=4)
        FooClass().method("foo", arg2=1)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(AssertionError, "FooClass.method('foo', arg2=4) call not found"):
            State.teardown()

    def test_mock_instance_method_all_calls_with(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").all_calls_with("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        State.teardown()

        # Extra argument
        mocker(FooClass).mock("method").all_calls_with("foo")
        FooClass().method("foo", arg2=2)
        with assert_raises(
            AssertionError,
            (
                "All calls have not been made with the given arguments:\n"
                "Arguments: call('foo')\n"
                "Calls: [call('foo', arg2=2)]."
            ),
        ):
            State.teardown()

        mocker(FooClass).mock("method").all_calls_with("foo", arg2=2)
        FooClass().method("foo", arg2=2)
        FooClass().method("foo", arg2=1)
        FooClass().method("foo", arg2=2)
        with assert_raises(
            AssertionError,
            (
                "All calls have not been made with the given arguments:\n"
                "Arguments: call('foo', arg2=2)\n"
                "Calls: [call('foo', arg2=2), call('foo', arg2=1), call('foo', arg2=2)]."
            ),
        ):
            State.teardown()

        mocker(FooClass).mock("method").all_calls_with("bar", arg2=3)
        FooClass().method("bar", arg2=3)
        FooClass().method("foo", arg2=3)
        FooClass().method("bar", arg2=3)
        with assert_raises(
            AssertionError,
            (
                "All calls have not been made with the given arguments:\n"
                "Arguments: call('bar', arg2=3)\n"
                "Calls: [call('bar', arg2=3), call('foo', arg2=3), call('bar', arg2=3)]."
            ),
        ):
            State.teardown()

    def test_mock_instance_method_match_args_any_call(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").match_args_any_call("bar")
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_any_call(arg2=3)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_any_call("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_any_call("foo")
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No call includes arguments:\n"
            "Arguments: call('foo')\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_any_call(arg2=1)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No call includes arguments:\n"
            "Arguments: call(arg2=1)\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_any_call("foo", arg2=1)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No call includes arguments:\n"
            "Arguments: call('foo', arg2=1)\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

    def test_mock_instance_method_match_args_all_calls(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").match_args_all_calls("bar")
        FooClass().method("bar", arg2=2)
        FooClass().method("bar", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_all_calls(arg2=3)
        FooClass().method("bar", arg2=3)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_all_calls("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        State.teardown()

        mocker(FooClass).mock("method").match_args_all_calls("foo")
        FooClass().method("foo", arg2=2)
        FooClass().method("bar", arg2=3)
        with assert_raises(
            AssertionError,
            "All calls do not contain the given arguments:\n"
            "Arguments: call('foo')\n"
            "Calls: [call('foo', arg2=2), call('bar', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_all_calls(arg2=1)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=1)
        with assert_raises(
            AssertionError,
            "All calls do not contain the given arguments:\n"
            "Arguments: call(arg2=1)\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=1)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_all_calls("foo", arg2=1)
        FooClass().method("foo", arg2=1)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "All calls do not contain the given arguments:\n"
            "Arguments: call('foo', arg2=1)\n"
            "Calls: [call('foo', arg2=1), call('baz', arg2=3)].",
        ):
            State.teardown()

    def test_mock_instance_method_match_args_last_call(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").match_args_last_call("baz")
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_last_call(arg2=3)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_last_call("baz", arg2=3)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_last_call("bar")
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "Last call does not include arguments:\n"
            "Arguments: call('bar')\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_last_call(arg2=2)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "Last call does not include arguments:\n"
            "Arguments: call(arg2=2)\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_last_call("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "Last call does not include arguments:\n"
            "Arguments: call('bar', arg2=2)\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

    def test_mock_property_with_match_args(self) -> None:
        class FooClass:
            @property
            def prop(self) -> str:
                return "value"

        mocker(FooClass).mock("prop").return_value("mocked").match_args_any_call()
        assert FooClass().prop == "mocked"
        State.teardown()
        assert FooClass().prop == "value"

        mocker(FooClass).mock("prop").return_value("mocked").match_args_any_call("bar")
        assert FooClass().prop == "mocked"
        with assert_raises(
            AssertionError,
            "No call includes arguments:\nArguments: call('bar')\nCalls: [call()].",
        ):
            State.teardown()
        assert FooClass().prop == "value"

        mocker(FooClass).mock("prop").return_value("mocked").match_args_all_calls()
        assert FooClass().prop == "mocked"
        State.teardown()
        assert FooClass().prop == "value"

        mocker(FooClass).mock("prop").return_value("mocked").match_args_all_calls("bar")
        assert FooClass().prop == "mocked"
        with assert_raises(
            AssertionError,
            "All calls do not contain the given arguments:\n"
            "Arguments: call('bar')\n"
            "Calls: [call()].",
        ):
            State.teardown()
        assert FooClass().prop == "value"

        mocker(FooClass).mock("prop").return_value("mocked").match_args_last_call()
        assert FooClass().prop == "mocked"
        State.teardown()
        assert FooClass().prop == "value"

        mocker(FooClass).mock("prop").return_value("mocked").match_args_last_call("bar")
        assert FooClass().prop == "mocked"
        with assert_raises(
            AssertionError,
            "Last call does not include arguments:\nArguments: call('bar')\nCalls: [call()].",
        ):
            State.teardown()
        assert FooClass().prop == "value"

    def test_mock_instance_method_has_calls(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").has_calls([call("bar", arg2=2)])
        FooClass().method("bar", arg2=2)
        State.teardown()

        mocker(FooClass).mock("method").has_calls([call("bar", arg2=2)])
        FooClass().method("foo", arg2=1)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            re.compile(
                r"Calls not found.\n"
                r"Expected: \[call\('bar', arg2=2\)\]\n"
                r"\s*Actual: \[call\('foo', arg2=1\), call\('baz', arg2=3\)\]"
            ),
        ):
            State.teardown()

    def test_mock_instance_method_not_called(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").not_called()
        State.teardown()

        mocker(FooClass).mock("method").not_called()
        FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to not have been called. Called 1 times.\nCalls: [call()].",
        ):
            State.teardown()

    def test_mock_instance_method_called(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").called()
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").called()
        with assert_raises(AssertionError, "Expected 'FooClass.method' to have been called."):
            State.teardown()

    def test_mock_instance_method_called_once(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").called_once()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to have been called once. Called 0 times.",
        ):
            State.teardown()

    def test_mock_instance_method_called_twice(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").called_twice()
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").called_twice()
        FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to have been called twice. Called once.\nCalls: [call()].",
        ):
            State.teardown()

    def test_mock_instance_method_call_count(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").call_count(3)
        FooClass().method()
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").call_count(3)
        FooClass().method()
        FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to have been called 3 times. "
            "Called twice.\nCalls: [call(), call()].",
        ):
            State.teardown()

    def test_mock_instance_method_call_count_at_least(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").call_count_at_least(3)
        FooClass().method()
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").call_count_at_least(3)
        FooClass().method()
        FooClass().method()
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").call_count_at_least(3)
        FooClass().method()
        FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to have been called at least 3 times. "
            "Called twice.\nCalls: [call(), call()].",
        ):
            State.teardown()

    def test_mock_instance_method_call_count_at_most(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").call_count_at_most(3)
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").call_count_at_most(3)
        FooClass().method()
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").call_count_at_most(3)
        FooClass().method()
        FooClass().method()
        FooClass().method()
        FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to have been called at most 3 times. "
            "Called 4 times.\nCalls: [call(), call(), call(), call()].",
        ):
            State.teardown()

    def test_mock_instance_method_call_count_at_most_and_at_most(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method").call_count_at_least(2).call_count_at_most(3)
        FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to have been called at least twice. "
            "Called once.\nCalls: [call()].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").call_count_at_least(2).call_count_at_most(3)
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").call_count_at_least(2).call_count_at_most(3)
        FooClass().method()
        FooClass().method()
        FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").call_count_at_least(2).call_count_at_most(3)
        FooClass().method()
        FooClass().method()
        FooClass().method()
        FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'FooClass.method' to have been called at most 3 times. "
            "Called 4 times.\nCalls: [call(), call(), call(), call()].",
        ):
            State.teardown()

    def test_mock_empty_attribute_name(self) -> None:
        with assert_raises(ValueError, "Attribute name cannot be empty."):
            mocker(SomeClass).mock("")
        with assert_raises(ValueError, "Attribute name cannot be empty."):
            mocker(SomeClass).mock("instance_method.")

    def test_mock_runtime_class_attribute(self) -> None:
        class FooClass:
            pass

        FooClass.method = lambda: "foo"  # type: ignore
        assert FooClass.method() == "foo"  # type: ignore
        mocker(FooClass).mock("method").return_value("mocked").called_once()
        assert FooClass.method() == "mocked"  # type: ignore
        State.teardown()
        assert FooClass.method() == "foo"  # type: ignore

    def test_mock_instance_attribute(self) -> None:
        instance = SomeClass()
        assert instance.attr == "instance_attr"
        mocker(instance).mock("attr").return_value("mocked")
        assert instance.attr == "mocked"
        State.teardown()
        assert instance.attr == "instance_attr"

    def test_mock_runtime_instance_attribute(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        class FooClass:
            pass

        FooClass.method1 = lambda self: "foo"  # type: ignore
        instance = FooClass()
        instance.method2 = lambda: "bar"  # type: ignore
        assert instance.method1() == "foo"  # type: ignore
        assert instance.method2() == "bar"  # type: ignore
        mocker(instance).mock("method1").return_value("mocked1").called_once()
        mocker(instance).mock("method2").return_value("mocked2").called_once()
        assert instance.method1() == "mocked1"  # type: ignore
        assert instance.method2() == "mocked2"  # type: ignore
        State.teardown()
        assert instance.method1() == "foo"  # type: ignore
        assert instance.method2() == "bar"  # type: ignore

    def test_mock_non_existing_attribute(self) -> None:
        # pylint: disable=no-member
        class FooClass:
            pass

        mocker(FooClass).mock("method", create=True).return_value("mocked").called_twice()
        assert FooClass.method() == "mocked"  # type: ignore
        assert FooClass().method() == "mocked"  # type: ignore

    def test_mock_non_existing_attribute_fail(self) -> None:
        class FooClass:
            pass

        with assert_raises(AttributeError, "type object 'FooClass' has no attribute 'method'"):
            mocker(FooClass).mock("method", create=False)

    def test_mock_proxied_class_instance_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        SomeClassProxy = Proxy(SomeClass)
        mocker(SomeClassProxy).mock("instance_method_with_args").return_value(3).called_once_with(1)
        assert SomeClassProxy().instance_method_with_args(1) == 3  # type: ignore

    def test_mock_proxied_class_class_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        SomeClassProxy = Proxy(SomeClass)
        mocker(SomeClassProxy).mock("class_method_with_args").return_value(3).has_calls(
            [call(1), call(2)]
        )
        assert SomeClassProxy().class_method_with_args(1) == 3  # type: ignore
        assert SomeClassProxy.class_method_with_args(2) == 3

    def test_mock_proxied_class_static_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        SomeClassProxy = Proxy(SomeClass)
        mocker(SomeClassProxy).mock("static_method_with_args").return_value(3).has_calls(
            [call(1), call(2)]
        )
        assert SomeClassProxy().static_method_with_args(1) == 3  # type: ignore
        assert SomeClassProxy.static_method_with_args(2) == 3

    def test_mock_proxied_derived_instance_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        DerivedClassProxy = Proxy(DerivedClass)
        mocker(DerivedClassProxy).mock("instance_method_with_args").return_value(
            3
        ).called_once_with(1)
        assert DerivedClassProxy().instance_method_with_args(1) == 3  # type: ignore

    def test_mock_proxied_derived_class_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        DerivedClassProxy = Proxy(DerivedClass)
        mocker(DerivedClassProxy).mock("class_method_with_args").return_value(3).has_calls(
            [call(1), call(2)]
        )
        assert DerivedClassProxy().class_method_with_args(1) == 3  # type: ignore
        assert DerivedClassProxy.class_method_with_args(2) == 3

    def test_mock_proxied_derived_static_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        DerivedClassProxy = Proxy(DerivedClass)
        mocker(DerivedClassProxy).mock("static_method_with_args").return_value(3).has_calls(
            [call(1), call(2)]
        )
        assert DerivedClassProxy().static_method_with_args(1) == 3  # type: ignore
        assert DerivedClassProxy.static_method_with_args(2) == 3

    def test_mock_proxied_module_function_with_args(self) -> None:
        # pylint: disable=not-callable
        common_proxy = Proxy(common)
        mocker(common_proxy).mock("some_function").return_value(3).called_once_with(1)
        assert common_proxy.some_function(1) == 3

    def test_mock_private_instance_method(self) -> None:
        # pylint: disable=protected-access
        mocker(SomeClass).mock("_private").return_value("mocked").called_once()
        assert SomeClass()._private() == "mocked"
        State.teardown()
        assert SomeClass()._private() == "private_value"

    def test_mock_private_mangled_instance_method(self) -> None:
        # pylint: disable=protected-access
        mocker(SomeClass).mock("__very_private").return_value("mocked").called_once()
        assert SomeClass()._SomeClass__very_private() == "mocked"  # type: ignore
        State.teardown()
        assert SomeClass()._SomeClass__very_private() == "very_private_value"  # type: ignore

        instance = SomeClass()
        mocker(instance).mock("__very_private").return_value("mocked").called_once()
        assert instance._SomeClass__very_private() == "mocked"  # type: ignore
        State.teardown()
        assert instance._SomeClass__very_private() == "very_private_value"  # type: ignore

    def test_mock_global_module_variable(self) -> None:
        mocker(common).mock("GLOBAL_VARIABLE").return_value("mocked")
        assert common.GLOBAL_VARIABLE == "mocked"
        State.teardown()
        assert common.GLOBAL_VARIABLE == "global_value"

    def test_mock_call_method(self) -> None:
        class FooClass:
            def __call__(self) -> str:
                return "called"

        instance = FooClass()
        mocker(FooClass).mock("__call__").return_value("mocked").called_once()
        assert instance() == "mocked"
        State.teardown()
        assert instance() == "called"

    def test_mock_call_async_assert_with_non_async_method(self) -> None:
        for method_name in ["not_awaited", "awaited_once", "awaited", "awaited_twice"]:
            mocked = mocker(SomeClass).mock("instance_method")
            with assert_raises(
                AttributeError,
                f"MagicMock does not have '{method_name}' method. "
                "You can use 'force_async' parameter to force the mock to be an AsyncMock.",
            ):
                getattr(mocked, method_name)()

    def test_mock_builtin_function(self) -> None:
        mocker(sys.stdout).mock("write").return_value(123).called_once()
        assert sys.stdout.write("foo") == 123
        State.teardown()

        mocker(sys.stdout).mock("write").return_value(123).called_once()
        sys.stdout.write("foo")
        sys.stdout.write("bar")
        with assert_raises(
            AssertionError,
            re.compile(
                # Pytest wraps TextIoWrapper with EncodedFile
                r"Expected '(EncodedFile|TextIOWrapper).write' to have been called once. "
                r"Called twice.\n"
                r"Calls: \[call\('foo'\), call\('bar'\)\]."
            ),
        ):
            State.teardown()

    def test_mock_context_manager(self) -> None:
        class FooContextManager:
            def __enter__(self) -> str:
                return "enter"

            def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
                pass

        mocker(FooContextManager).mock("__enter__").return_value("mocked").called_once()
        with FooContextManager() as value:
            assert value == "mocked"
        State.teardown()
        with FooContextManager() as value:
            assert value == "enter"

    def test_mock_builtin_open(self) -> None:
        mock_file = mocker()
        mock_file.mock("read").return_value("mocked1").called_once()
        mocker(builtins).mock("open").return_value(mock_file)
        # pylint: disable=consider-using-with
        assert open("foo", encoding="utf8").read() == "mocked1"

        State.teardown()

        mock_file = mocker()
        mock_file.mock("read").return_value("mocked2").called_once()
        mock_open = mocker("builtins.open").get_mock()
        mock_open.return_value.__enter__ = mock_file

        with open("file_name", encoding="utf8") as file:
            assert file.read() == "mocked2"

    def test_mock_builtin_called_once_with(self) -> None:
        # pylint: disable=unreachable
        mocker(sys).mock("exit").called_once_with(123)
        sys.exit(123)
        State.teardown()

        mocker(sys).mock("exit").called_once_with(123)
        sys.exit(1)
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: sys.exit\(123\)\n"
                r"\s*Actual: sys.exit\(1\)"
            ),
        ):
            State.teardown()

    def test_mock_class_attribute(self) -> None:
        mocker(SomeClass).mock("ATTR").return_value("mocked").called_once()
        assert SomeClass.ATTR == "mocked"
        State.teardown()
        assert SomeClass.ATTR == "class_attr"
