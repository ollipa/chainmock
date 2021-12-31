"""Test async mocking functionality."""
# pylint: disable=missing-docstring,no-self-use
import pytest

from chainmock import mocker
from chainmock._api import State
from chainmock.mock import call

from . import common
from .common import SomeClass
from .utils import assert_raises


class TestAsyncMocking:
    @pytest.mark.asyncio
    async def test_mock_async_function_return_value(self) -> None:
        mocker(common).mock("some_async_function").return_value("async_mocked")
        assert await common.some_async_function("foo") == "async_mocked"
        State.teardown()
        assert await common.some_async_function("foo") == "foo"

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_return_value(self) -> None:
        mocker(SomeClass).mock("async_instance_method").return_value("instance_mocked")
        assert await SomeClass().async_instance_method() == "instance_mocked"
        State.teardown()
        assert await SomeClass().async_instance_method() == "instance_attr"

    @pytest.mark.asyncio
    async def test_mock_async_class_method_return_value(self) -> None:
        mocker(SomeClass).mock("async_class_method").return_value("class_mocked")
        assert await SomeClass.async_class_method() == "class_mocked"
        assert await SomeClass().async_class_method() == "class_mocked"
        State.teardown()
        assert await SomeClass.async_class_method() == "class_attr"
        assert await SomeClass().async_class_method() == "class_attr"

    @pytest.mark.asyncio
    async def test_mock_async_static_method_return_value(self) -> None:
        mocker(SomeClass).mock("async_static_method").return_value("static_mocked")
        assert await SomeClass.async_static_method() == "static_mocked"
        assert await SomeClass().async_static_method() == "static_mocked"
        State.teardown()
        assert await SomeClass.async_static_method() == "static_value"
        assert await SomeClass().async_static_method() == "static_value"

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_awaited_last_with(self) -> None:
        class FooClass:
            async def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").awaited_last_with("foo", arg2=5)
        await FooClass().method("foo", arg2=5)
        State.teardown()

        mocker(FooClass).mock("method").awaited_last_with("foo", arg2=5)
        await FooClass().method("foo", arg2=10)
        with assert_raises(
            AssertionError,
            (
                "expected await not found.\n"
                "Expected: method('foo', arg2=5)\n"
                "Actual: method('foo', arg2=10)"
            ),
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_awaited_once_with(self) -> None:
        class FooClass:
            async def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").awaited_once_with("foo", arg2=5)
        await FooClass().method("foo", arg2=5)
        State.teardown()

        mocker(FooClass).mock("method").awaited_once_with("foo", arg2=5)
        await FooClass().method("bar", arg2=5)
        with assert_raises(
            AssertionError,
            (
                "expected await not found.\n"
                "Expected: method('foo', arg2=5)\n"
                "Actual: method('bar', arg2=5)"
            ),
        ):
            State.teardown()

        mocker(FooClass).mock("method").awaited_once_with("foo", arg2=5)
        await FooClass().method("foo", arg2=5)
        await FooClass().method("foo", arg2=5)
        with assert_raises(
            AssertionError,
            "Expected method to have been awaited once. Awaited 2 times.",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_any_await_with(self) -> None:
        class FooClass:
            async def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").any_await_with("bar", arg2=2)
        await FooClass().method("foo", arg2=1)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").any_await_with("foo", arg2=4)
        await FooClass().method("foo", arg2=1)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "method('foo', arg2=4) await not found",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_instance_method_match_args_any_await(self) -> None:
        class FooClass:
            async def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").match_args_any_await("bar")
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_any_await(arg2=3)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_any_await("bar", arg2=2)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_any_await("foo")
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No await includes arguments:\n"
            "Arguments: call('foo')\n"
            "Awaits: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_any_await(arg2=1)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No await includes arguments:\n"
            "Arguments: call(arg2=1)\n"
            "Awaits: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_any_await("foo", arg2=1)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "No await includes arguments:\n"
            "Arguments: call('foo', arg2=1)\n"
            "Awaits: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_instance_method_match_args_last_await(self) -> None:
        class FooClass:
            async def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").match_args_last_await("baz")
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_last_await(arg2=3)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_last_await("baz", arg2=3)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        State.teardown()

        mocker(FooClass).mock("method").match_args_last_await("bar")
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "Last await does not include arguments:\n"
            "Arguments: call('bar')\n"
            "Awaits: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_last_await(arg2=2)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "Last await does not include arguments:\n"
            "Arguments: call(arg2=2)\n"
            "Awaits: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

        mocker(FooClass).mock("method").match_args_last_await("bar", arg2=2)
        await FooClass().method("bar", arg2=2)
        await FooClass().method("baz", arg2=3)
        with assert_raises(
            AssertionError,
            "Last await does not include arguments:\n"
            "Arguments: call('bar', arg2=2)\n"
            "Awaits: [call('bar', arg2=2), call('baz', arg2=3)].",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_has_awaits(self) -> None:
        class FooClass:
            async def method(self, arg1: str, arg2: int = 10) -> str:
                return arg1 + str(arg2)

        mocker(FooClass).mock("method").has_awaits([call("foo", arg2=1), call("bar", arg2=2)])
        await FooClass().method("foo", arg2=1)
        await FooClass().method("bar", arg2=2)
        State.teardown()

        mocker(FooClass).mock("method").has_awaits([call("foo", arg2=1), call("bar", arg2=2)])
        await FooClass().method("bar", arg2=2)
        await FooClass().method("foo", arg2=1)
        with assert_raises(
            AssertionError,
            (
                "Awaits not found.\n"
                "Expected: [call('foo', arg2=1), call('bar', arg2=2)]\n"
                "Actual: [call('bar', arg2=2), call('foo', arg2=1)]"
            ),
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_not_awaited(self) -> None:
        class FooClass:
            async def method(self) -> None:
                pass

        mocker(FooClass).mock("method").not_awaited()
        State.teardown()

        mocker(FooClass).mock("method").not_awaited()
        await FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected method to not have been awaited. Awaited 1 times.",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_awaited(self) -> None:
        class FooClass:
            async def method(self) -> None:
                pass

        mocker(FooClass).mock("method").awaited()
        await FooClass().method()
        await FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").awaited()
        with assert_raises(AssertionError, "Expected method to have been awaited."):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_awaited_once(self) -> None:
        class FooClass:
            async def method(self) -> None:
                pass

        mocker(FooClass).mock("method").awaited_once()
        await FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").awaited_once()
        with assert_raises(
            AssertionError, "Expected 'method' to have been awaited once. Awaited 0 times."
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_awaited_twice(self) -> None:
        class FooClass:
            async def method(self) -> None:
                pass

        mocker(FooClass).mock("method").awaited_twice()
        await FooClass().method()
        await FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").awaited_twice()
        await FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'method' to have been awaited twice. Awaited once.\nAwaits: [call()].",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_await_count(self) -> None:
        class FooClass:
            async def method(self) -> None:
                pass

        mocker(FooClass).mock("method").await_count(3)
        await FooClass().method()
        await FooClass().method()
        await FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").await_count(3)
        await FooClass().method()
        await FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'method' to have been awaited 3 times. "
            "Awaited twice.\nAwaits: [call(), call()].",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_await_count_at_least(self) -> None:
        class FooClass:
            async def method(self) -> None:
                pass

        mocker(FooClass).mock("method").await_count_at_least(3)
        await FooClass().method()
        await FooClass().method()
        await FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").await_count_at_least(3)
        await FooClass().method()
        await FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'method' to have been awaited at least 3 times. "
            "Awaited twice.\nAwaits: [call(), call()].",
        ):
            State.teardown()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_await_count_at_most(self) -> None:
        class FooClass:
            async def method(self) -> None:
                pass

        mocker(FooClass).mock("method").await_count_at_most(3)
        await FooClass().method()
        await FooClass().method()
        await FooClass().method()
        State.teardown()

        mocker(FooClass).mock("method").await_count_at_most(3)
        await FooClass().method()
        await FooClass().method()
        await FooClass().method()
        await FooClass().method()
        with assert_raises(
            AssertionError,
            "Expected 'method' to have been awaited at most 3 times. "
            "Awaited 4 times.\nAwaits: [call(), call(), call(), call()].",
        ):
            State.teardown()
