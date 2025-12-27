"""Test spying functionality."""

import re

from chainmock import mocker
from chainmock._api import State

from . import common
from .common import SomeClass
from .utils import assert_raises


class AsyncSpyingTestCase:
    async def test_async_spy_function_called_once(self) -> None:
        mocker(common).spy("some_async_function").called_once()
        assert await common.some_async_function("foo") == "foo"
        State.teardown()
        assert await common.some_async_function("foo") == "foo"

    async def test_async_spy_function_called_once_fail(self) -> None:
        mocker(common).spy("some_async_function").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'tests.common.some_async_function' to have been called once. Called 0 times.",
        ):
            State.teardown()

    async def test_async_spy_function_called_once_with(self) -> None:
        mocker(common).spy("some_async_function").called_once_with("foo")
        assert await common.some_async_function("foo") == "foo"
        State.teardown()
        assert await common.some_async_function("foo") == "foo"

    async def test_async_spy_function_called_once_with_fail(self) -> None:
        mocker(common).spy("some_async_function").called_once_with("foo")
        assert await common.some_async_function("bar") == "bar"
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: tests.common.some_async_function\('foo'\)\n"
                r"\s*Actual: tests.common.some_async_function\('bar'\)"
            ),
        ):
            State.teardown()

    async def test_async_spy_class_call_instance_method_called_once(self) -> None:
        mocker(SomeClass).spy("async_instance_method").called_once()
        assert await SomeClass().async_instance_method() == "instance_attr"
        State.teardown()
        assert await SomeClass().async_instance_method() == "instance_attr"

    async def test_async_spy_class_call_instance_method_called_once_fail(self) -> None:
        mocker(SomeClass).spy("async_instance_method").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.async_instance_method' to have been called once. Called 0 times.",
        ):
            State.teardown()

    async def test_async_spy_class_call_instance_method_called_once_with(self) -> None:
        mocker(SomeClass).spy("async_instance_method_with_args").called_once_with(1)
        assert await SomeClass().async_instance_method_with_args(1) == 1
        State.teardown()
        assert await SomeClass().async_instance_method_with_args(2) == 2

    async def test_async_spy_class_call_instance_method_called_once_with_fail(
        self,
    ) -> None:
        mocker(SomeClass).spy("async_instance_method_with_args").called_once_with(1)
        assert await SomeClass().async_instance_method_with_args(2) == 2
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: SomeClass.async_instance_method_with_args\(1\)\n"
                r"\s*Actual: SomeClass.async_instance_method_with_args\(2\)"
            ),
        ):
            State.teardown()

    async def test_async_spy_instance_call_instance_method_called_once(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_instance_method").called_once()
        assert await instance.async_instance_method() == "instance_attr"
        State.teardown()
        assert await instance.async_instance_method() == "instance_attr"

    async def test_async_spy_instance_call_instance_method_called_once_fail(
        self,
    ) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_instance_method").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.async_instance_method' to have been called once. Called 0 times.",
        ):
            State.teardown()

    async def test_async_spy_instance_call_instance_method_called_once_with(
        self,
    ) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_instance_method_with_args").called_once_with(1)
        assert await instance.async_instance_method_with_args(1) == 1
        State.teardown()
        assert await instance.async_instance_method_with_args(2) == 2

    async def test_async_spy_instance_call_instance_method_called_once_with_fail(
        self,
    ) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_instance_method_with_args").called_once_with(1)
        assert await instance.async_instance_method_with_args(2) == 2
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: SomeClass.async_instance_method_with_args\(1\)\n"
                r"\s*Actual: SomeClass.async_instance_method_with_args\(2\)"
            ),
        ):
            State.teardown()

    async def test_async_spy_class_call_class_method_called_once(self) -> None:
        mocker(SomeClass).spy("async_class_method").called_once()
        assert await SomeClass.async_class_method() == "class_attr"
        State.teardown()
        assert await SomeClass.async_class_method() == "class_attr"

    async def test_async_spy_class_call_class_method_called_once_fail(self) -> None:
        mocker(SomeClass).spy("async_class_method").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.async_class_method' to have been called once. Called 0 times.",
        ):
            State.teardown()

    async def test_async_spy_class_call_class_method_called_once_with(self) -> None:
        mocker(SomeClass).spy("async_class_method_with_args").called_once_with(2)
        assert await SomeClass.async_class_method_with_args(2) == 2
        State.teardown()
        assert await SomeClass.async_class_method_with_args(2) == 2

    async def test_async_spy_class_call_class_method_called_once_with_fail(
        self,
    ) -> None:
        mocker(SomeClass).spy("async_class_method_with_args").called_once_with(2)
        assert await SomeClass.async_class_method_with_args(3) == 3
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: SomeClass.async_class_method_with_args\(2\)\n"
                r"\s*Actual: SomeClass.async_class_method_with_args\(3\)"
            ),
        ):
            State.teardown()

    async def test_async_spy_class_call_class_method_on_instance_called_once(
        self,
    ) -> None:
        mocker(SomeClass).spy("async_class_method").called_once()
        assert await SomeClass().async_class_method() == "class_attr"
        State.teardown()
        assert await SomeClass().async_class_method() == "class_attr"

    async def test_async_spy_class_call_class_method_on_instance_called_once_with(
        self,
    ) -> None:
        mocker(SomeClass).spy("async_class_method_with_args").called_once_with(2)
        assert await SomeClass().async_class_method_with_args(2) == 2
        State.teardown()
        assert await SomeClass().async_class_method_with_args(2) == 2

    async def test_async_spy_instance_call_class_method_called_once(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_class_method").called_once()
        assert await instance.async_class_method() == "class_attr"
        State.teardown()
        assert await instance.async_class_method() == "class_attr"

    async def test_async_spy_instance_call_class_method_called_once_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_class_method").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.async_class_method' to have been called once. Called 0 times.",
        ):
            State.teardown()

    async def test_async_spy_instance_call_class_method_called_once_with(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_class_method_with_args").called_once_with(2)
        assert await instance.async_class_method_with_args(2) == 2
        State.teardown()
        assert await instance.async_class_method_with_args(2) == 2

    async def test_async_spy_instance_call_class_method_called_once_with_fail(
        self,
    ) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_class_method_with_args").called_once_with(2)
        assert await instance.async_class_method_with_args(3) == 3
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: SomeClass.async_class_method_with_args\(2\)\n"
                r"\s*Actual: SomeClass.async_class_method_with_args\(3\)"
            ),
        ):
            State.teardown()

    async def test_async_spy_class_call_static_method_called_once(self) -> None:
        mocker(SomeClass).spy("async_static_method").called_once()
        assert await SomeClass.async_static_method() == "static_value"
        State.teardown()
        assert await SomeClass.async_static_method() == "static_value"

    async def test_async_spy_class_call_static_method_called_once_fail(self) -> None:
        mocker(SomeClass).spy("async_static_method").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.async_static_method' to have been called once. Called 0 times.",
        ):
            State.teardown()

    async def test_async_spy_class_call_static_method_called_once_with(self) -> None:
        mocker(SomeClass).spy("async_static_method_with_args").called_once_with(3)
        assert await SomeClass.async_static_method_with_args(3) == 3
        State.teardown()
        assert await SomeClass.async_static_method_with_args(3) == 3

    async def test_async_spy_class_call_static_method_called_once_with_fail(
        self,
    ) -> None:
        mocker(SomeClass).spy("async_static_method_with_args").called_once_with(3)
        assert await SomeClass.async_static_method_with_args(4) == 4
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: SomeClass.async_static_method_with_args\(3\)\n"
                r"\s*Actual: SomeClass.async_static_method_with_args\(4\)"
            ),
        ):
            State.teardown()

    async def test_async_spy_class_call_static_method_on_instance_called_once(
        self,
    ) -> None:
        mocker(SomeClass).spy("async_static_method").called_once()
        assert await SomeClass().async_static_method() == "static_value"
        State.teardown()
        assert await SomeClass().async_static_method() == "static_value"

    async def test_async_spy_class_call_static_method_on_instance_called_once_with(
        self,
    ) -> None:
        mocker(SomeClass).spy("async_static_method_with_args").called_once_with(3)
        assert await SomeClass().async_static_method_with_args(3) == 3
        State.teardown()
        assert await SomeClass().async_static_method_with_args(3) == 3

    async def test_async_spy_instance_call_static_method_called_once(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_static_method").called_once()
        assert await instance.async_static_method() == "static_value"
        State.teardown()
        assert await instance.async_static_method() == "static_value"

    async def test_async_spy_instance_call_static_method_called_once_fail(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_static_method").called_once()
        with assert_raises(
            AssertionError,
            "Expected 'SomeClass.async_static_method' to have been called once. Called 0 times.",
        ):
            State.teardown()

    async def test_async_spy_instance_call_static_method_called_once_with(self) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_static_method_with_args").called_once_with(3)
        assert await instance.async_static_method_with_args(3) == 3
        State.teardown()
        assert await instance.async_static_method_with_args(3) == 3

    async def test_async_spy_instance_call_static_method_called_once_with_fail(
        self,
    ) -> None:
        instance = SomeClass()
        mocker(instance).spy("async_static_method_with_args").called_once_with(3)
        assert await instance.async_static_method_with_args(4) == 4
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: SomeClass.async_static_method_with_args\(3\)\n"
                r"\s*Actual: SomeClass.async_static_method_with_args\(4\)"
            ),
        ):
            State.teardown()
