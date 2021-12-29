"""Test patching functionality."""
# pylint: disable=missing-docstring,no-self-use
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

    @classmethod
    def class_method(cls) -> str:
        return cls.ATTR

    @staticmethod
    def static_method() -> str:
        return "static_value"


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

    def test_patching_chaining_methods(self) -> None:
        mocker("tests.test_patching.First").mock("get_second.get_third.method").return_value(
            "mock_chain"
        )
        assert First().get_second().get_third().method() == "mock_chain"
        State.teardown()
        assert First().get_second().get_third().method() == "value"

    def test_patch_non_existing_attribute(self) -> None:
        # pylint: disable=no-member

        mocker("tests.test_patching.PatchClass").mock("foo_method", create=True).return_value(
            "mocked"
        ).called_once()
        assert PatchClass().foo_method() == "mocked"  # type: ignore

    def test_patch_non_existing_attribute_fail(self) -> None:

        with assert_raises(AttributeError, "Mock object has no attribute 'foo_method'"):
            mocker("tests.test_patching.PatchClass").mock("foo_method", create=False)
