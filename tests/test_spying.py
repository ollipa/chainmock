"""Test spying functionality."""
# pylint: disable=missing-docstring,no-self-use
from chainmock import mocker
from chainmock._api import State

from . import common
from .common import SomeClass
from .utils import assert_raises


class TestSpying:
    def test_spy_stub_should_fail(self) -> None:
        with assert_raises(RuntimeError, "Spying is not available for stubs. Call 'mock' instead."):
            mocker().spy("instance_method")

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
