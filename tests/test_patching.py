"""Test patching functionality."""
# pylint: disable=missing-docstring,no-self-use
from chainmock import mocker
from chainmock._api import State


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


class TestPatching:
    # def test_patching_instance_method_return_value(self) -> None:
    #     mocker("__main__.PatchClass").mock("instance_method").return_value("mocked")
    #     assert PatchClass().instance_method() == "mocked"
    #     State.teardown()
    #     assert PatchClass().instance_method() == "instance_attr"

    def test_patching_class_method_return_value(self) -> None:
        mocker("tests.test_patching.PatchClass").mock("class_method").return_value("mocked")
        assert PatchClass.class_method() == "mocked"
        State.teardown()
        assert PatchClass.class_method() == "class_attr"

    def test_patching_static_method_return_value(self) -> None:
        mocker("tests.test_patching.PatchClass").mock("static_method").return_value("mocked")
        assert PatchClass.static_method() == "mocked"
        State.teardown()
        assert PatchClass.static_method() == "static_value"
