"""Test spying functionality."""
# pylint: disable=missing-docstring,no-self-use
import re

from chainmock import mocker
from chainmock._api import State
from chainmock.mock import call

from . import common
from .common import DerivedClass, Proxy, SomeClass
from .utils import assert_raises


class TestSpying:  # pylint: disable=too-many-public-methods
    def test_spy_should_cache_asserts(self) -> None:
        assert1 = mocker(SomeClass).spy("instance_method")
        assert2 = mocker(SomeClass).spy("instance_method")
        assert assert1 is assert2

    def test_spy_stub_should_fail(self) -> None:
        with assert_raises(RuntimeError, "Spying is not available for stubs. Call 'mock' instead."):
            mocker().spy("instance_method")

    def test_spy_patched_object_should_fail(self) -> None:
        with assert_raises(
            RuntimeError, "Spying is not available for patched objects. Call 'mock' instead."
        ):
            mocker("tests.common.SomeClass").spy("instance_method")

    def test_spy_with_empty_attribute_name_should_fail(self) -> None:
        with assert_raises(ValueError, "Attribute name cannot be empty."):
            mocker(SomeClass).spy("")

    def test_spy_function_called_once(self) -> None:
        mocker(common).spy("some_function").called_once()
        assert common.some_function("foo") == "foo"
        State.teardown()
        assert common.some_function("foo") == "foo"

    def test_spy_function_called_once_fail(self) -> None:
        mocker(common).spy("some_function").called_once()
        with assert_raises(
            AssertionError, "Expected 'some_function' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_function_called_once_with(self) -> None:
        mocker(common).spy("some_function").called_once_with("foo")
        assert common.some_function("foo") == "foo"
        State.teardown()
        assert common.some_function("foo") == "foo"

    def test_spy_function_called_once_with_fail(self) -> None:
        mocker(common).spy("some_function").called_once_with("foo")
        assert common.some_function("bar") == "bar"
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: some_function('foo')\n"
            "Actual: some_function('bar')",
        ):
            State.teardown()

    def test_spy_class_call_instance_method_called_once(self) -> None:
        mocker(SomeClass).spy("instance_method").called_once()
        assert SomeClass().instance_method() == "instance_attr"
        State.teardown()
        assert SomeClass().instance_method() == "instance_attr"

    def test_spy_class_call_instance_method_called_once_fail(self) -> None:
        mocker(SomeClass).spy("instance_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'instance_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_class_call_instance_method_called_once_with(self) -> None:
        mocker(SomeClass).spy("instance_method_with_args").called_once_with(1)
        assert SomeClass().instance_method_with_args(1) == 1
        State.teardown()
        assert SomeClass().instance_method_with_args(2) == 2

    def test_spy_class_call_instance_method_called_once_with_fail(self) -> None:
        mocker(SomeClass).spy("instance_method_with_args").called_once_with(1)
        assert SomeClass().instance_method_with_args(2) == 2
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: instance_method_with_args(1)\n"
            "Actual: instance_method_with_args(2)",
        ):
            State.teardown()

    def test_spy_instance_call_instance_method_called_once(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("instance_method").called_once()
        assert instance.instance_method() == "instance_attr"
        State.teardown()
        assert instance.instance_method() == "instance_attr"

    def test_spy_instance_call_instance_method_called_once_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("instance_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'instance_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_instance_call_instance_method_called_once_with(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("instance_method_with_args").called_once_with(1)
        assert instance.instance_method_with_args(1) == 1
        State.teardown()
        assert instance.instance_method_with_args(2) == 2

    def test_spy_instance_call_instance_method_called_once_with_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("instance_method_with_args").called_once_with(1)
        assert instance.instance_method_with_args(2) == 2
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: instance_method_with_args(1)\n"
            "Actual: instance_method_with_args(2)",
        ):
            State.teardown()

    def test_spy_class_call_class_method_called_once(self) -> None:
        mocker(SomeClass).spy("class_method").called_once()
        assert SomeClass.class_method() == "class_attr"
        State.teardown()
        assert SomeClass.class_method() == "class_attr"

    def test_spy_class_call_class_method_called_once_fail(self) -> None:
        mocker(SomeClass).spy("class_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'class_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_class_call_class_method_called_once_with(self) -> None:
        mocker(SomeClass).spy("class_method_with_args").called_once_with(2)
        assert SomeClass.class_method_with_args(2) == 2
        State.teardown()
        assert SomeClass.class_method_with_args(2) == 2

    def test_spy_class_call_class_method_called_once_with_fail(self) -> None:
        mocker(SomeClass).spy("class_method_with_args").called_once_with(2)
        assert SomeClass.class_method_with_args(3) == 3
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: class_method_with_args(2)\n"
            "Actual: class_method_with_args(3)",
        ):
            State.teardown()

    def test_spy_class_call_class_method_on_instance_called_once(self) -> None:
        mocker(SomeClass).spy("class_method").called_once()
        assert SomeClass().class_method() == "class_attr"
        State.teardown()
        assert SomeClass().class_method() == "class_attr"

    def test_spy_class_call_class_method_on_instance_called_once_with(self) -> None:
        mocker(SomeClass).spy("class_method_with_args").called_once_with(2)
        assert SomeClass().class_method_with_args(2) == 2
        State.teardown()
        assert SomeClass().class_method_with_args(2) == 2

    def test_spy_instance_call_class_method_called_once(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("class_method").called_once()
        assert instance.class_method() == "class_attr"
        State.teardown()
        assert instance.class_method() == "class_attr"

    def test_spy_instance_call_class_method_called_once_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("class_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'class_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_instance_call_class_method_called_once_with(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("class_method_with_args").called_once_with(2)
        assert instance.class_method_with_args(2) == 2
        State.teardown()
        assert instance.class_method_with_args(2) == 2

    def test_spy_instance_call_class_method_called_once_with_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("class_method_with_args").called_once_with(2)
        assert instance.class_method_with_args(3) == 3
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: class_method_with_args(2)\n"
            "Actual: class_method_with_args(3)",
        ):
            State.teardown()

    def test_spy_class_call_static_method_called_once(self) -> None:
        mocker(SomeClass).spy("static_method").called_once()
        assert SomeClass.static_method() == "static_value"
        State.teardown()
        assert SomeClass.static_method() == "static_value"

    def test_spy_class_call_static_method_called_once_fail(self) -> None:
        mocker(SomeClass).spy("static_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'static_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_class_call_static_method_called_once_with(self) -> None:
        mocker(SomeClass).spy("static_method_with_args").called_once_with(3)
        assert SomeClass.static_method_with_args(3) == 3
        State.teardown()
        assert SomeClass.static_method_with_args(3) == 3

    def test_spy_class_call_static_method_called_once_with_fail(self) -> None:
        mocker(SomeClass).spy("static_method_with_args").called_once_with(3)
        assert SomeClass.static_method_with_args(4) == 4
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: static_method_with_args(3)\n"
            "Actual: static_method_with_args(4)",
        ):
            State.teardown()

    def test_spy_class_call_static_method_on_instance_called_once(self) -> None:
        mocker(SomeClass).spy("static_method").called_once()
        assert SomeClass().static_method() == "static_value"
        State.teardown()
        assert SomeClass().static_method() == "static_value"

    def test_spy_class_call_static_method_on_instance_called_once_with(self) -> None:
        mocker(SomeClass).spy("static_method_with_args").called_once_with(3)
        assert SomeClass().static_method_with_args(3) == 3
        State.teardown()
        assert SomeClass().static_method_with_args(3) == 3

    def test_spy_instance_call_static_method_called_once(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("static_method").called_once()
        assert instance.static_method() == "static_value"
        State.teardown()
        assert instance.static_method() == "static_value"

    def test_spy_instance_call_static_method_called_once_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("static_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'static_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_instance_call_static_method_called_once_with(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("static_method_with_args").called_once_with(3)
        assert instance.static_method_with_args(3) == 3
        State.teardown()
        assert instance.static_method_with_args(3) == 3

    def test_spy_instance_call_static_method_called_once_with_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("static_method_with_args").called_once_with(3)
        assert instance.static_method_with_args(4) == 4
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: static_method_with_args(3)\n"
            "Actual: static_method_with_args(4)",
        ):
            State.teardown()

    def test_spy_instance_call_instance_method_called_once_with_too_many_args(self) -> None:
        # pylint: disable=too-many-function-args
        class FooClass:
            def method(self, arg1: int, arg2: str) -> str:
                del arg1
                del arg2
                return "value"

        instance = FooClass()
        mocker(instance).spy("method").called_once_with(1, "foo")
        with assert_raises(
            TypeError, re.compile(r".*method\(\) takes 3 positional arguments but 4 were given")
        ):
            instance.method(2, 1, "foo")  # type: ignore
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: method(1, 'foo')\n"
            "Actual: method(2, 1, 'foo')",
        ):
            State.teardown()

    def test_spy_derived_class_call_instance_method_called_once(self) -> None:
        mocker(DerivedClass).spy("instance_method").called_once()
        assert DerivedClass().instance_method() == "instance_attr"
        State.teardown()
        assert DerivedClass().instance_method() == "instance_attr"

    def test_spy_derived_class_call_instance_method_called_once_fail(self) -> None:
        mocker(DerivedClass).spy("instance_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'instance_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_derived_class_call_instance_method_called_once_with(self) -> None:
        mocker(DerivedClass).spy("instance_method_with_args").called_once_with(1)
        assert DerivedClass().instance_method_with_args(1) == 1
        State.teardown()
        assert DerivedClass().instance_method_with_args(2) == 2

    def test_spy_derived_class_call_instance_method_called_once_with_fail(self) -> None:
        mocker(DerivedClass).spy("instance_method_with_args").called_once_with(1)
        assert DerivedClass().instance_method_with_args(2) == 2
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: instance_method_with_args(1)\n"
            "Actual: instance_method_with_args(2)",
        ):
            State.teardown()

    def test_spy_derived_instance_call_instance_method_called_once(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("instance_method").called_once()
        assert instance.instance_method() == "instance_attr"
        State.teardown()
        assert instance.instance_method() == "instance_attr"

    def test_spy_derived_instance_call_instance_method_called_once_fail(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("instance_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'instance_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_derived_instance_call_instance_method_called_once_with(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("instance_method_with_args").called_once_with(1)
        assert instance.instance_method_with_args(1) == 1
        State.teardown()
        assert instance.instance_method_with_args(2) == 2

    def test_spy_derived_instance_call_instance_method_called_once_with_fail(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("instance_method_with_args").called_once_with(1)
        assert instance.instance_method_with_args(2) == 2
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: instance_method_with_args(1)\n"
            "Actual: instance_method_with_args(2)",
        ):
            State.teardown()

    def test_spy_derived_class_call_class_method_called_once(self) -> None:
        mocker(DerivedClass).spy("class_method").called_once()
        assert DerivedClass.class_method() == "class_attr"
        State.teardown()
        assert DerivedClass.class_method() == "class_attr"

    def test_spy_derived_class_call_class_method_called_once_fail(self) -> None:
        mocker(DerivedClass).spy("class_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'class_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_derived_class_call_class_method_called_once_with(self) -> None:
        mocker(DerivedClass).spy("class_method_with_args").called_once_with(2)
        assert DerivedClass.class_method_with_args(2) == 2
        State.teardown()
        assert DerivedClass.class_method_with_args(2) == 2

    def test_spy_derived_class_call_class_method_called_once_with_fail(self) -> None:
        mocker(DerivedClass).spy("class_method_with_args").called_once_with(2)
        assert DerivedClass.class_method_with_args(3) == 3
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: class_method_with_args(2)\n"
            "Actual: class_method_with_args(3)",
        ):
            State.teardown()

    def test_spy_derived_class_call_class_method_on_instance_called_once(self) -> None:
        mocker(DerivedClass).spy("class_method").called_once()
        assert DerivedClass().class_method() == "class_attr"
        State.teardown()
        assert DerivedClass().class_method() == "class_attr"

    def test_spy_derived_class_call_class_method_on_instance_called_once_with(self) -> None:
        mocker(DerivedClass).spy("class_method_with_args").called_once_with(2)
        assert DerivedClass().class_method_with_args(2) == 2
        State.teardown()
        assert DerivedClass().class_method_with_args(2) == 2

    def test_spy_derived_instance_call_class_method_called_once(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("class_method").called_once()
        assert instance.class_method() == "class_attr"
        State.teardown()
        assert instance.class_method() == "class_attr"

    def test_spy_derived_instance_call_class_method_called_once_fail(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("class_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'class_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_derived_instance_call_class_method_called_once_with(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("class_method_with_args").called_once_with(2)
        assert instance.class_method_with_args(2) == 2
        State.teardown()
        assert instance.class_method_with_args(2) == 2

    def test_spy_derived_instance_call_class_method_called_once_with_fail(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("class_method_with_args").called_once_with(2)
        assert instance.class_method_with_args(3) == 3
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: class_method_with_args(2)\n"
            "Actual: class_method_with_args(3)",
        ):
            State.teardown()

    def test_spy_derived_class_call_static_method_called_once(self) -> None:
        mocker(DerivedClass).spy("static_method").called_once()
        assert DerivedClass.static_method() == "static_value"
        State.teardown()
        assert DerivedClass.static_method() == "static_value"

    def test_spy_derived_class_call_static_method_called_once_fail(self) -> None:
        mocker(DerivedClass).spy("static_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'static_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_derived_class_call_static_method_called_once_with(self) -> None:
        mocker(DerivedClass).spy("static_method_with_args").called_once_with(3)
        assert DerivedClass.static_method_with_args(3) == 3
        State.teardown()
        assert DerivedClass.static_method_with_args(3) == 3

    def test_spy_derived_class_call_static_method_called_once_with_fail(self) -> None:
        mocker(DerivedClass).spy("static_method_with_args").called_once_with(3)
        assert DerivedClass.static_method_with_args(4) == 4
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: static_method_with_args(3)\n"
            "Actual: static_method_with_args(4)",
        ):
            State.teardown()

    def test_spy_derived_class_call_static_method_on_instance_called_once(self) -> None:
        mocker(DerivedClass).spy("static_method").called_once()
        assert DerivedClass().static_method() == "static_value"
        State.teardown()
        assert DerivedClass().static_method() == "static_value"

    def test_spy_derived_class_call_static_method_on_instance_called_once_with(self) -> None:
        mocker(DerivedClass).spy("static_method_with_args").called_once_with(3)
        assert DerivedClass().static_method_with_args(3) == 3
        State.teardown()
        assert DerivedClass().static_method_with_args(3) == 3

    def test_spy_derived_instance_call_static_method_called_once(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("static_method").called_once()
        assert instance.static_method() == "static_value"
        State.teardown()
        assert instance.static_method() == "static_value"

    def test_spy_derived_instance_call_static_method_called_once_fail(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("static_method").called_once()
        with assert_raises(
            AssertionError, "Expected 'static_method' to have been called once. Called 0 times."
        ):
            State.teardown()

    def test_spy_derived_instance_call_static_method_called_once_with(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("static_method_with_args").called_once_with(3)
        assert instance.static_method_with_args(3) == 3
        State.teardown()
        assert instance.static_method_with_args(3) == 3

    def test_spy_derived_instance_call_static_method_called_once_with_fail(self) -> None:
        instance = DerivedClass()
        mocker(instance).spy("static_method_with_args").called_once_with(3)
        assert instance.static_method_with_args(4) == 4
        with assert_raises(
            AssertionError,
            "expected call not found.\n"
            "Expected: static_method_with_args(3)\n"
            "Actual: static_method_with_args(4)",
        ):
            State.teardown()

    def test_spy_class_and_instance(self) -> None:
        instance = SomeClass()
        mocker(SomeClass).spy("instance_method").called_twice()
        SomeClass().instance_method()
        mocker(instance).spy("instance_method").called_once()
        instance.instance_method()
        State.teardown()

        mocker(SomeClass).spy("instance_method").called_twice()
        SomeClass().instance_method()
        instance = SomeClass()
        mocker(instance).spy("instance_method").called_once()
        instance.instance_method()
        State.teardown()

        instance = SomeClass()
        mocker(instance).spy("instance_method").called_once()
        instance.instance_method()
        mocker(SomeClass).spy("instance_method").called_once()
        SomeClass().instance_method()
        State.teardown()

    def test_spy_class_and_derived_class(self) -> None:
        mocker(SomeClass).spy("instance_method").called_twice()
        SomeClass().instance_method()
        mocker(DerivedClass).spy("instance_method").called_once()
        DerivedClass().instance_method()
        State.teardown()

        mocker(SomeClass).spy("instance_method").called_twice()
        SomeClass().instance_method()
        mocker(DerivedClass).spy("instance_method").called_once()
        DerivedClass().instance_method()
        State.teardown()

        mocker(DerivedClass).spy("instance_method").called_once()
        DerivedClass().instance_method()
        mocker(SomeClass).spy("instance_method").called_once()
        SomeClass().instance_method()
        State.teardown()

    def test_spy_proxied_class_instance_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        SomeClassProxy = Proxy(SomeClass)
        mocker(SomeClassProxy).spy("instance_method_with_args").called_once_with(1)
        assert SomeClassProxy().instance_method_with_args(1) == 1  # type: ignore

    def test_spy_proxied_class_class_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        SomeClassProxy = Proxy(SomeClass)
        mocker(SomeClassProxy).spy("class_method_with_args").has_calls([call(1), call(2)])
        assert SomeClassProxy().class_method_with_args(1) == 1  # type: ignore
        assert SomeClassProxy.class_method_with_args(2) == 2

    def test_spy_proxied_class_static_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        SomeClassProxy = Proxy(SomeClass)
        mocker(SomeClassProxy).spy("static_method_with_args").has_calls([call(1), call(2)])
        assert SomeClassProxy().static_method_with_args(1) == 1  # type: ignore
        assert SomeClassProxy.static_method_with_args(2) == 2

    def test_spy_proxied_derived_instance_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        DerivedClassProxy = Proxy(DerivedClass)
        mocker(DerivedClassProxy).spy("instance_method_with_args").called_once_with(1)
        assert DerivedClassProxy().instance_method_with_args(1) == 1  # type: ignore

    def test_spy_proxied_derived_class_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        DerivedClassProxy = Proxy(DerivedClass)
        mocker(DerivedClassProxy).spy("class_method_with_args").has_calls([call(1), call(2)])
        assert DerivedClassProxy().class_method_with_args(1) == 1  # type: ignore
        assert DerivedClassProxy.class_method_with_args(2) == 2

    def test_spy_proxied_derived_static_method_with_args(self) -> None:
        # pylint: disable=not-callable,invalid-name
        DerivedClassProxy = Proxy(DerivedClass)
        mocker(DerivedClassProxy).spy("static_method_with_args").has_calls([call(1), call(2)])
        assert DerivedClassProxy().static_method_with_args(1) == 1  # type: ignore
        assert DerivedClassProxy.static_method_with_args(2) == 2

    def test_spy_proxied_module_function_with_args(self) -> None:
        # pylint: disable=not-callable
        common_proxy = Proxy(common)
        mocker(common_proxy).spy("some_function").called_once_with(1)
        assert common_proxy.some_function(1) == 1

    def test_spy_private_instance_method(self) -> None:
        # pylint: disable=protected-access
        mocker(SomeClass).spy("_private").called_once()
        assert SomeClass()._private() == "private_value"
        State.teardown()
        assert SomeClass()._private() == "private_value"

    def test_spy_private_mangled_instance_method(self) -> None:
        # pylint: disable=protected-access
        mocker(SomeClass).spy("__very_private").called_once()
        assert SomeClass()._SomeClass__very_private() == "very_private_value"  # type: ignore
        State.teardown()
        assert SomeClass()._SomeClass__very_private() == "very_private_value"  # type: ignore

        instance = SomeClass()
        mocker(instance).spy("__very_private").called_once()
        assert instance._SomeClass__very_private() == "very_private_value"  # type: ignore
        State.teardown()
        assert instance._SomeClass__very_private() == "very_private_value"  # type: ignore
