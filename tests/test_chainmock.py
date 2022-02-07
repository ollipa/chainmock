"""Test common functionality in Chainmock."""
# pylint: disable=missing-docstring,no-self-use
from chainmock._api import Assert, Mock, State, mocker

from .utils import assert_raises


class TestChainmock:
    def test_return_self_when_called(self) -> None:
        stub = mocker()
        assert stub() is stub

    def test_init_mock_directly_should_fail(self) -> None:
        with assert_raises(
            RuntimeError, "Mock should not be initialized directly. Use mocker function instead."
        ):
            Mock()

    def test_init_assert_directly_should_fail(self) -> None:
        with assert_raises(
            RuntimeError, "Assert should not be initialized directly. Use mocker function instead."
        ):
            mock = mocker()
            Assert(mock, None)

    def test_mocker_should_cache_mocks(self) -> None:
        class FooClass:
            pass

        mock1 = mocker(FooClass)
        mock2 = mocker(FooClass)
        assert mock1 is mock2

        mock1 = mocker(FooClass())
        mock2 = mocker(FooClass())
        assert mock1 is not mock2

        instance1 = FooClass()
        instance2 = FooClass()
        mock1 = mocker(instance1)
        mock2 = mocker(instance2)
        assert mock1 is not mock2

        mock1 = mocker("tests.common.SomeClass")
        mock2 = mocker("tests.common.SomeClass")
        assert mock1 is mock2

    def test_mocking_and_spying_same_attribute(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        mocker(FooClass).mock("method")
        with assert_raises(
            RuntimeError,
            "Attribute 'method' has already been mocked. Can't spy a mocked attribute.",
        ):
            mocker(FooClass).spy("method")
        State.teardown()

        mocker(FooClass).spy("method")
        with assert_raises(
            RuntimeError, "Attribute 'method' has already been spied. Can't mock a spied attribute."
        ):
            mocker(FooClass).mock("method")
        State.teardown()

    def test_get_mock(self) -> None:
        class FooClass:
            def method(self) -> None:
                pass

        instance = FooClass()
        mock = mocker(instance).mock("method").get_mock()
        mock.assert_not_called()
        instance.method()
        mock.assert_called_once()
