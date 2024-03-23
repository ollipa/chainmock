"""Test stubbing functionality."""

# pylint: disable=missing-docstring
import re

from chainmock._api import Mock, State, mocker

from .common import SomeClass
from .utils import assert_raises


class StubbingTestCase:
    def test_stubbing(self) -> None:
        stub = mocker().mock("method").called_once_with("foo").return_value("stubbed").self()
        assert stub.method("foo") == "stubbed"  # type: ignore [attr-defined]

    def test_stubbing_arguments_fail(self) -> None:
        stub = mocker().mock("method").called_once_with("foo").return_value("stubbed").self()
        assert stub.method("bar") == "stubbed"  # type: ignore [attr-defined]
        with assert_raises(
            AssertionError,
            re.compile(
                r"expected call not found.\n"
                r"Expected: Stub.method\('foo'\)\n"
                r"\s*Actual: Stub.method\('bar'\)"
            ),
        ):
            State.teardown()

    def test_stubbing_call_count_fail(self) -> None:
        stub = mocker().mock("method").called_twice().return_value("stubbed").self()
        assert stub.method() == "stubbed"  # type: ignore [attr-defined]
        with assert_raises(
            AssertionError,
            "Expected 'Stub.method' to have been called twice. Called once.\nCalls: [call()].",
        ):
            State.teardown()

    def test_stubbing_internal_attribute(self) -> None:
        with assert_raises(ValueError, "Cannot replace Mock internal attribute _reset"):
            mocker().mock("_reset").return_value("stubbed").self()

    def test_stub_chaining(self) -> None:
        stub = mocker().mock("method.another_method").return_value("stubbed").self()
        assert stub.method().another_method() == "stubbed"  # type: ignore [attr-defined]

    async def test_stub_async_method(self) -> None:
        stub = mocker(spec=SomeClass).mock("async_instance_method").return_value("stubbed").self()
        assert await stub.async_instance_method() == "stubbed"  # type: ignore [attr-defined]
        stub = mocker(spec=SomeClass).mock("async_class_method").return_value("stubbed").self()
        assert await stub.async_class_method() == "stubbed"  # type: ignore [attr-defined]
        stub = mocker(spec=SomeClass).mock("async_static_method").return_value("stubbed").self()
        assert await stub.async_static_method() == "stubbed"  # type: ignore [attr-defined]

    async def test_stub_force_async(self) -> None:
        stub = mocker(spec=SomeClass)
        stub.mock("instance_method", force_async=True).return_value("stubbed").called_once()
        assert await stub.instance_method() == "stubbed"  # type: ignore [attr-defined]

    async def test_stub_force_async_no_spec(self) -> None:
        stub = mocker()
        stub.mock("some_method", force_async=True).return_value("stubbed").called_once()
        assert await stub.some_method() == "stubbed"  # type: ignore [attr-defined]

    async def test_stub_force_async_non_existing_attribute(self) -> None:
        stub = mocker(spec=SomeClass)
        stub.mock("unknown_attr", create=True, force_async=True).return_value(
            "stubbed"
        ).called_once()
        assert await stub.unknown_attr() == "stubbed"  # type: ignore [attr-defined]

    def test_stubs_are_not_cached(self) -> None:
        stub1 = mocker()
        stub2 = mocker()
        assert stub1 is not stub2

    def test_stub_kwargs_without_spec(self) -> None:
        stub = mocker(some_property="foo", instance_method="bar")
        assert stub.some_property == "foo"  # type: ignore [attr-defined]
        assert stub.instance_method == "bar"  # type: ignore [attr-defined]

    def test_stub_kwargs_with_spec(self) -> None:
        stub = mocker(some_property="foo", instance_method=lambda: "bar", spec=SomeClass)
        assert stub.some_property == "foo"  # type: ignore [attr-defined]
        assert stub.instance_method() == "bar"  # type: ignore [attr-defined]

    def test_stub_property_without_spec(self) -> None:
        stub = mocker()
        stub.mock("some_property", force_property=True).called_once().return_value("foo")
        assert stub.some_property == "foo"  # type: ignore [attr-defined]
        stub.mock("some_method", force_property=False).called_once_with("bar").return_value("baz")
        assert stub.some_method("bar") == "baz"  # type: ignore [attr-defined]

    def test_stub_property_with_spec(self) -> None:
        stub = mocker(spec=SomeClass)
        stub.mock("some_property").called_once().return_value("foo")
        assert stub.some_property == "foo"  # type: ignore [attr-defined]
        stub.mock("instance_method").called_once_with("bar").return_value("baz")
        assert stub.instance_method("bar") == "baz"  # type: ignore [attr-defined]

    def test_stub_property_with_spec_force_property(self) -> None:
        stub = mocker(spec=SomeClass)
        stub.mock("instance_method", force_property=True).called_once().return_value("foo")
        assert stub.instance_method == "foo"  # type: ignore [attr-defined]

    def test_stub_property_call_count_fail(self) -> None:
        stub = mocker(spec=SomeClass)
        stub.mock("some_property").called_twice().return_value("foo")
        assert stub.some_property == "foo"  # type: ignore [attr-defined]
        with assert_raises(
            AssertionError,
            "Expected 'Stub.some_property' to have been called twice. Called once.\n"
            "Calls: [call()].",
        ):
            State.teardown()

    def test_stub_properties_not_attached_to_mock_class(self) -> None:
        """Intermediary class should be used to attach properties."""
        stub = mocker(some_property="foo", spec=SomeClass)
        assert stub.some_property == "foo"  # type: ignore [attr-defined]
        assert not hasattr(Mock, "some_property")

    def test_stub_non_existing_attributes(self) -> None:
        stub = mocker(spec=SomeClass)
        stub.mock("unknown_attr", create=True).return_value("foo")
        assert stub.unknown_attr() == "foo"  # type: ignore [attr-defined]
        stub.mock("unknown_property", create=True, force_property=True).return_value("bar")
        assert stub.unknown_property == "bar"  # type: ignore [attr-defined]

        with assert_raises(
            AttributeError, "type object 'SomeClass' has no attribute 'unknown_attr'"
        ):
            mocker(unknown_attr="foo", spec=SomeClass)

        with assert_raises(
            AttributeError, "type object 'SomeClass' has no attribute 'unknown_attr'"
        ):
            stub = mocker(spec=SomeClass)
            stub.mock("unknown_attr")

    def test_stub_with_list_spec(self) -> None:
        stub = mocker(spec=["foo"])
        stub.mock("foo").return_value("foo")
        assert stub.foo() == "foo"  # type: ignore [attr-defined]
        with assert_raises(AttributeError, "Mock object has no attribute 'bar'"):
            stub.mock("bar").return_value("bar")

        stub = mocker(spec=("baz",))
        stub.mock("baz").return_value("baz")
        assert stub.baz() == "baz"  # type: ignore [attr-defined]
        with assert_raises(AttributeError, "Mock object has no attribute 'qux'"):
            stub.mock("qux").return_value("qux")

    def test_stub_isinstance_checks(self) -> None:
        stub = mocker(spec=SomeClass)
        assert isinstance(stub, SomeClass)
        assert isinstance(stub, Mock)

        instance = SomeClass()
        stub = mocker(spec=instance)
        assert isinstance(stub, SomeClass)
        assert isinstance(stub, Mock)

        stub = mocker()
        assert not isinstance(stub, SomeClass)
        assert isinstance(stub, Mock)

        stub = mocker(spec=["foo", "bar"])
        assert not isinstance(stub, SomeClass)
        assert isinstance(stub, Mock)

        stub = mocker(spec=("foo", "bar"))
        assert not isinstance(stub, SomeClass)
        assert isinstance(stub, Mock)
