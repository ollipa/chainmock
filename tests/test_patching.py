"""Test patching functionality."""
# pylint: disable=missing-docstring
from typing import Type

from chainmock import mocker
from chainmock._api import State

from .utils import assert_raises


class PatchClass:
    ATTR = "class_attr"

    def __init__(self) -> None:
        self.attr = "instance_attr"

    def instance_method(self) -> str:
        return self.attr

    def instance_method_with_args(self, arg1: int) -> int:
        return arg1

    async def async_instance_method(self) -> str:
        return self.attr

    @classmethod
    def class_method(cls) -> str:
        return cls.ATTR

    @staticmethod
    def static_method() -> str:
        return "static_value"

    @property
    def some_property(self) -> str:
        return self.attr


class Third:
    @classmethod
    def method(cls) -> str:
        return "value"

    @classmethod
    async def async_method(cls) -> str:
        return "value"


class Second:
    def get_third(self) -> Type[Third]:
        return Third

    @property
    def prop(self) -> str:
        return "value"


class First:
    def get_second(self) -> Second:
        return Second()


class TestPatching:
    def test_patching_should_cache_asserts(self) -> None:
        assert1 = mocker("tests.test_patching.PatchClass").mock("instance_method")
        assert2 = mocker("tests.test_patching.PatchClass").mock("instance_method")
        assert assert1 is assert2

    def test_patching_instance_method_return_value(self) -> None:
        mocker("tests.test_patching.PatchClass").mock("instance_method").return_value("mocked")
        assert PatchClass().instance_method() == "mocked"
        State.teardown()
        assert PatchClass().instance_method() == "instance_attr"

    def test_patching_class_method_return_value(self) -> None:
        mocker("tests.test_patching.PatchClass", patch_class=True).mock(
            "class_method"
        ).return_value("mocked")
        assert PatchClass.class_method() == "mocked"
        State.teardown()
        assert PatchClass.class_method() == "class_attr"

    def test_patching_class_method_return_value_on_an_instance(self) -> None:
        mocker("tests.test_patching.PatchClass").mock("class_method").return_value("mocked")
        assert PatchClass().class_method() == "mocked"
        State.teardown()
        assert PatchClass().class_method() == "class_attr"

    def test_patching_static_method_return_value(self) -> None:
        mocker("tests.test_patching.PatchClass", patch_class=True).mock(
            "static_method"
        ).return_value("mocked")
        assert PatchClass.static_method() == "mocked"
        State.teardown()
        assert PatchClass.static_method() == "static_value"

    def test_patching_static_method_return_value_on_an_instance(self) -> None:
        mocker("tests.test_patching.PatchClass").mock("static_method").return_value("mocked")
        assert PatchClass().static_method() == "mocked"
        State.teardown()
        assert PatchClass().static_method() == "static_value"

    def test_patching_chained_methods(self) -> None:
        mocker("tests.test_patching.First").mock("get_second.get_third.method").return_value(
            "mock_chain"
        )
        assert First().get_second().get_third().method() == "mock_chain"
        State.teardown()
        assert First().get_second().get_third().method() == "value"

    def test_patching_chained_property(self) -> None:
        mocker("tests.test_patching.First").mock(
            "get_second.prop", force_property=True
        ).return_value("mock_chain")
        assert First().get_second().prop == "mock_chain"
        State.teardown()
        assert First().get_second().prop == "value"

    async def test_patching_chained_async_methods(self) -> None:
        mocker("tests.test_patching.First").mock(
            "get_second.get_third.async_method", force_async=True
        ).return_value("mock_chain")
        assert await First().get_second().get_third().async_method() == "mock_chain"
        State.teardown()
        assert await First().get_second().get_third().async_method() == "value"

    def test_patch_non_existing_attribute(self) -> None:
        # pylint: disable=no-member

        mocker("tests.test_patching.PatchClass").mock("foo_method", create=True).return_value(
            "mocked"
        ).called_once()
        assert PatchClass().foo_method() == "mocked"  # type: ignore

    def test_patch_non_existing_attribute_fail(self) -> None:

        with assert_raises(AttributeError, "Mock object has no attribute 'foo_method'"):
            mocker("tests.test_patching.PatchClass").mock("foo_method", create=False)

    def test_patching_call_count(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("instance_method").called_once().return_value("mocked")
        assert PatchClass().instance_method() == "mocked"

    def test_patching_call_count_fail(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("instance_method").called_twice().return_value("mocked")
        assert PatchClass().instance_method() == "mocked"
        with assert_raises(
            AssertionError,
            "Expected 'instance_method' to have been called twice. Called once.\nCalls: [call()].",
        ):
            State.teardown()

    def test_patching_with_args(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("instance_method_with_args").called_once_with(1).return_value(2)
        assert PatchClass().instance_method_with_args(1) == 2

    def test_patching_with_args_fail(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("instance_method_with_args").called_once_with(1).return_value(2)
        assert PatchClass().instance_method_with_args(2) == 2
        with assert_raises(
            AssertionError,
            (
                "expected call not found.\nExpected: instance_method_with_args(1)\n"
                "Actual: instance_method_with_args(2)"
            ),
        ):
            State.teardown()

    def test_patching_property(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("some_property").called_once().return_value("mocked")
        assert PatchClass().some_property == "mocked"
        State.teardown()
        assert PatchClass().some_property == "instance_attr"

    def test_patching_force_property(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("instance_method", force_property=True).called_once().return_value("mocked")
        # pylint: disable=comparison-with-callable
        assert PatchClass().instance_method == "mocked"  # type: ignore
        State.teardown()
        assert PatchClass().instance_method() == "instance_attr"

    def test_patching_create_unknown_property(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("unknown_property", force_property=True, create=True).return_value("mocked")
        # pylint: disable=no-member
        assert PatchClass().unknown_property == "mocked"  # type: ignore
        assert hasattr(PatchClass(), "unknown_property")
        State.teardown()
        assert not hasattr(PatchClass(), "unknown_property")

    async def test_patching_async_method(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("async_instance_method").return_value("patched").called_once()
        assert await PatchClass().async_instance_method() == "patched"

    async def test_patching_force_async(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("instance_method", force_async=True).return_value("patched").called_once()
        assert await PatchClass().instance_method() == "patched"  # type: ignore

    async def test_patching_force_async_non_existing_attribute(self) -> None:
        mocked = mocker("tests.test_patching.PatchClass")
        mocked.mock("unknown_attr", create=True, force_async=True).return_value(
            "patched"
        ).called_once()
        # pylint: disable=no-member
        assert await PatchClass().unknown_attr() == "patched"  # type: ignore
