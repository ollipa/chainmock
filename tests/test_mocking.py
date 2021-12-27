"""Test mocking functionality."""
# pylint: disable=missing-docstring,no-self-use
from typing import Type

from chainmock import mocker
from chainmock._api import State
from chainmock.mock import call

from . import common
from .common import DerivedClass, Proxy, SomeClass
from .utils import assert_raises


class TestMocking:  # pylint: disable=too-many-public-methods
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
        mocker(DerivedClass).mock("instance_method_with_args").called_last_with(1).return_value(
            2
        ).called_once()
        assert DerivedClass().instance_method_with_args(1) == 2

    def test_mock_instance_method_on_derived_class_and_base_class_called_with_args(self) -> None:
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

    def test_mock_class_method_on_derived_class_and_base_class_called_with_args(self) -> None:
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

    def test_mock_static_method_on_derived_class_and_base_class_called_with_args(self) -> None:
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

        mocker(FooClass).mock("method").called_last_with("foo", arg2=5)
        FooClass().method("foo", arg2=10)
        with assert_raises(
            AssertionError,
            (
                "expected call not found.\n"
                "Expected: method('foo', arg2=5)\n"
                "Actual: method('foo', arg2=10)"
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
        with assert_raises(AssertionError, "method('foo', arg2=4) call not found"):
            State.teardown()

    def test_mock_instance_method_any_call_has_args(self) -> None:
        class FooClass:
            def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").any_call_has_args("bar")
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").any_call_has_args(arg2=3)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").any_call_has_args("bar", arg2=2)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").any_call_has_args("foo")
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No call includes arguments:\n"
            "Arguments: call('foo')\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").any_call_has_args(arg2=1)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No call includes arguments:\n"
            "Arguments: call(arg2=1)\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").any_call_has_args("foo", arg2=1)
        FooClass().method("bar", arg2=2)
        FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No call includes arguments:\n"
            "Arguments: call('foo', arg2=1)\n"
            "Calls: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

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
            "Calls not found.\nExpected: [call('bar', arg2=2)]\n"
            "Actual: [call('foo', arg2=1), call('baz', arg2=3)]",
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
            "Expected 'method' to not have been called. Called 1 times.\nCalls: [call()].",
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
        with assert_raises(AssertionError, "Expected 'method' to have been called."):
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
            AssertionError, "Expected 'method' to have been called once. Called 0 times."
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
            "Expected 'method' to have been called twice. Called once.\nCalls: [call()].",
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
            "Expected 'method' to have been called 3 times. "
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
            "Expected 'method' to have been called at least 3 times. "
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
            "Expected 'method' to have been called at most 3 times. "
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
            "Expected 'method' to have been called at least twice. "
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
            "Expected 'method' to have been called at most 3 times. "
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
