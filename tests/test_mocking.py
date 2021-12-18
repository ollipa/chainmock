"""Test mocking functionality."""
# pylint: disable=missing-docstring,no-self-use
import pytest

from mokit._api import MockerState, mocker


class SomeClass:
    ATTR = "class_attr"

    def __init__(self) -> None:
        self.attr = "instance_attr"

    def method(self) -> str:
        return self.attr

    @classmethod
    def class_method(cls) -> str:
        return cls.ATTR

    @staticmethod
    def staticmethod() -> str:
        return "static_value"


class TestMocking:
    def test_mock_chaining(self) -> None:
        class FooClass:
            def method(self) -> str:
                return "value"

        assert FooClass().method() == "value"
        mocker(FooClass).mock("method").return_value("mocked").called_once().self()
        assert FooClass().method() == "mocked"
        MockerState.reset()
        MockerState.teardown()
        assert FooClass().method() == "value"

    def test_mock_class(self) -> None:
        class FooClass:
            def method(self) -> str:
                return "value"

        mock = mocker(FooClass)
        mock.mock("method").return_value("mocked").called_once()
        assert FooClass().method() == "mocked"

    def test_stubbing(self) -> None:
        mocked = mocker().mock("method").return_value("mocked").called_once().self()
        assert mocked.method() == "mocked"  # type: ignore

    def test_mock_side_effect(self) -> None:
        class FooClass:
            def method(self) -> str:
                return "value"

        mocker(FooClass).mock("method").side_effect(RuntimeError("foo")).called_once()
        with pytest.raises(RuntimeError):
            assert FooClass().method() == "mocked"

    def test_mock_side_effect_multiple_return(self) -> None:
        class FooClass:
            def method(self) -> int:
                return 10

        mock = mocker(FooClass).mock("method").side_effect([1, 2, 3]).called_times(3).self()
        assert FooClass().method() == 1
        assert FooClass().method() == 2
        assert FooClass().method() == 3
        mock.teardown()

    def test_mock_call_with_args(self) -> None:
        class FooClass:
            def method(self, arg1: str) -> int:
                del arg1
                return 10

        mocker(FooClass).mock("method").return_value(1).called_once_with("broo")
        assert FooClass().method("broo") == 1

    def test_teardown_hook_part1(self) -> None:
        assert SomeClass().method() == "instance_attr"
        mocker(SomeClass).mock("method").return_value("mocked1")
        assert SomeClass().method() == "mocked1"

    def test_teardown_hook_part2(self) -> None:
        assert SomeClass().method() == "instance_attr"
        mocker(SomeClass).mock("method").return_value("mocked2")
        assert SomeClass().method() == "mocked2"

    @pytest.mark.xfail
    def test_teardown_hook_part3(self) -> None:
        assert SomeClass().method() == "instance_attr"
        mocker(SomeClass).mock("method").return_value("mocked3")
        assert SomeClass().method() == "mocked3"
        raise RuntimeError()

    def test_teardown_hook_part4(self) -> None:
        assert SomeClass().method() == "instance_attr"

    def test_mock_multiple_times(self) -> None:
        mocker(SomeClass).mock("method").return_value("mocked1")
        assert SomeClass().method() == "mocked1"
        mocker(SomeClass).mock("method").return_value("mocked2")
        assert SomeClass().method() == "mocked2"

    def test_mock_class_and_instance(self) -> None:
        class FooClass:
            def method(self) -> str:
                return "value"

        mocker(FooClass).mock("method").return_value("mocked1")
        assert FooClass().method() == "mocked1"
        instance = FooClass()
        mocker(instance).mock("method").return_value("mocked2")
        assert FooClass().method() == "mocked1"
        assert instance.method() == "mocked2"
        MockerState.reset()
        MockerState.teardown()
        assert FooClass().method() == "value"
        assert instance.method() == "value"

    def test_mock_static_and_class_methods(self) -> None:
        assert SomeClass().method() == "instance_attr"
        assert SomeClass.class_method() == "class_attr"
        assert SomeClass.staticmethod() == "static_value"

        mocker(SomeClass).mock("method").return_value("mocked1")
        mocker(SomeClass).mock("class_method").return_value("mocked2")
        mocker(SomeClass).mock("staticmethod").return_value("mocked3")

        assert SomeClass().method() == "mocked1"
        assert SomeClass.class_method() == "mocked2"
        assert SomeClass.staticmethod() == "mocked3"
