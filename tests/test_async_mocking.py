"""Test async mocking functionality."""
# pylint: disable=missing-docstring,no-self-use
import pytest

from chainmock import mocker
from chainmock._api import State

from .common import SomeClass
from .utils import assert_raises


class TestAsyncMocking:
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
    async def test_mock_async_instance_method_awaited_once(self) -> None:
        mocker(SomeClass).mock("async_instance_method").awaited_once()
        await SomeClass().async_instance_method()

    @pytest.mark.asyncio
    async def test_mock_async_instance_method_awaited_once_fail(self) -> None:
        mocker(SomeClass).mock("async_instance_method").awaited_once()
        with assert_raises(
            AssertionError,
            "Expected 'async_instance_method' to have been awaited once. Awaited 0 times.",
        ):
            State.teardown()
