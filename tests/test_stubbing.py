"""Test stubbing functionality."""
# pylint: disable=missing-docstring,no-self-use
import pytest

from chainmock import mocker

from .common import SomeClass
from .utils import assert_raises


class TestStubbing:
    def test_stubbing(self) -> None:
        stub = mocker().mock("method").return_value("stubbed").self()
        assert stub.method() == "stubbed"  # type: ignore

    def test_stubbing_internal_attribute(self) -> None:
        with assert_raises(ValueError, "Cannot replace Mock internal attribute _reset"):
            mocker().mock("_reset").return_value("stubbed").self()

    def test_stub_chaining(self) -> None:
        stub = mocker().mock("method.another_method").return_value("stubbed").self()
        assert stub.method().another_method() == "stubbed"  # type: ignore

    @pytest.mark.asyncio
    async def test_async_stub(self) -> None:
        stub = mocker(spec=SomeClass).mock("async_instance_method").return_value("stubbed").self()
        assert await stub.async_instance_method() == "stubbed"  # type: ignore
        stub = mocker(spec=SomeClass).mock("async_class_method").return_value("stubbed").self()
        assert await stub.async_class_method() == "stubbed"  # type: ignore
        stub = mocker(spec=SomeClass).mock("async_static_method").return_value("stubbed").self()
        assert await stub.async_static_method() == "stubbed"  # type: ignore
