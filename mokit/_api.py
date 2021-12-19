"""Mokit.

Spy, stub, and mock library for Python and Pytest.
"""
# pylint: disable=missing-docstring
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
from unittest import mock as umock

AnyMock = Union[umock.AsyncMock, umock.MagicMock, umock.PropertyMock]


class MockAssert:
    def __init__(self, parent: Mocker, attr_mock: AnyMock, name: str, _mokit: bool = False) -> None:
        if not _mokit:
            raise RuntimeError("MockAssert should not be initialized directly.")
        self._parent = parent
        self._attr_mock = attr_mock
        self._name = name
        self._assertions: List[Callable[..., None]] = []

    def return_value(self, value: Any) -> MockAssert:
        self._attr_mock.return_value = value
        return self

    def side_effect(self, value: Any) -> MockAssert:
        self._attr_mock.side_effect = value
        return self

    def called_with(self, *args: Any, **kwargs: Any) -> MockAssert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_called_with, *args, **kwargs)
        )
        return self

    def awaited_with(self, *args: Any, **kwargs: Any) -> MockAssert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_awaited_with, *args, **kwargs)
        )
        return self

    def called_once_with(self, *args: Any, **kwargs: Any) -> MockAssert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_called_once_with, *args, **kwargs)
        )
        return self

    def awaited_once_with(self, *args: Any, **kwargs: Any) -> MockAssert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_awaited_once_with, *args, **kwargs)
        )
        return self

    def any_call(self, *args: Any, **kwargs: Any) -> MockAssert:
        self._assertions.append(functools.partial(self._attr_mock.assert_any_call, *args, **kwargs))
        return self

    def any_await(self, *args: Any, **kwargs: Any) -> MockAssert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_any_await, *args, **kwargs)
        )
        return self

    def has_calls(self, calls: Sequence[umock._Call], any_order: bool = False) -> MockAssert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_has_calls, calls, any_order)
        )
        return self

    def has_awaits(self, calls: Sequence[umock._Call], any_order: bool = False) -> MockAssert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_has_awaits, calls, any_order)
        )
        return self

    def not_called(self) -> MockAssert:
        self._assertions.append(functools.partial(self._attr_mock.assert_not_called))
        return self

    def not_awaited(self) -> MockAssert:
        self._assertions.append(functools.partial(self._attr_mock.assert_not_awaited))
        return self

    def called(self) -> MockAssert:
        self._assertions.append(functools.partial(self._attr_mock.assert_called))
        return self

    def awaited(self) -> MockAssert:
        self._assertions.append(functools.partial(self._attr_mock.assert_awaited))
        return self

    def called_once(self) -> MockAssert:
        self._assertions.append(functools.partial(self._assert_call_count, 1))
        return self

    def awaited_once(self) -> MockAssert:
        self._assertions.append(functools.partial(self._assert_await_count, 1))
        return self

    def called_twice(self) -> MockAssert:
        self._assertions.append(functools.partial(self._assert_call_count, 2))
        return self

    def awaited_twice(self) -> MockAssert:
        self._assertions.append(functools.partial(self._assert_await_count, 2))
        return self

    def called_times(self, call_count: int) -> MockAssert:
        self._assertions.append(functools.partial(self._assert_call_count, call_count))
        return self

    def awaited_times(self, await_count: int) -> MockAssert:
        self._assertions.append(functools.partial(self._assert_await_count, await_count))
        return self

    def validate(self) -> None:
        while len(self._assertions) > 0:
            assertion = self._assertions.pop()
            assertion()

    def self(self) -> Mocker:
        return self._parent

    def _assert_await_count(self, await_count: int) -> None:
        if not self._attr_mock.await_count == await_count:
            if await_count == 1:
                times = "once"
            elif await_count == 2:
                times = "twice"
            else:
                times = f"{await_count} times"
            msg = (
                f"Expected '{self._name}' to have been awaited {times}. "
                f"Awaited {self._attr_mock.await_count} times."
            )
            raise AssertionError(msg)

    def _assert_call_count(self, call_count: int) -> None:
        if not self._attr_mock.call_count == call_count:
            if call_count == 1:
                times = "once"
            elif call_count == 2:
                times = "twice"
            else:
                times = f"{call_count} times"
            msg = (
                f"Expected '{self._name}' to have been called {times}. "
                f"Called {self._attr_mock.call_count} times.{self._attr_mock._calls_repr()}"  # pylint:disable=protected-access
            )
            raise AssertionError(msg)


class Mocker:
    def __init__(self, target: Any = None, *, _mokit: bool = False) -> None:
        if not _mokit:
            raise RuntimeError(
                "Mocker should not be initialized directly. Use mocker function instead."
            )
        self._target = target
        self._mock = umock.MagicMock(spec=target, wraps=target)
        self._assertions: List[MockAssert] = []
        self._originals: List[Tuple[Any, str]] = []
        self._overrides: List[str] = []

        MockerState.add_mocker(self, target)

    def spy(self, name: str) -> MockAssert:
        if self._target is None:
            raise RuntimeError("Stubs can not be spied. Did you mean to call mock()?")
        return self._attr_mock(name)

    def mock(self, name: str) -> MockAssert:
        assertion = self._attr_mock(name)
        assertion.return_value(None)
        return assertion

    def _attr_mock(self, name: str) -> MockAssert:
        parts = name.split(".")
        if not parts:
            raise ValueError("Method name can not be empty")
        name = parts[0]
        attr_mock: AnyMock = getattr(self._mock, name)
        if self._target is None:
            setattr(self, name, attr_mock)
        else:
            original = self._get_original(name)
            if isinstance(original, property):
                attr_mock = umock.PropertyMock()
            local_override = self._set_mocked_attribute(name, attr_mock)
            if local_override:
                self._overrides.append(name)
            elif name not in self._overrides and name not in [name for _, name in self._originals]:
                self._originals.append((original, name))
        assertion = MockAssert(self, attr_mock, name, _mokit=True)
        if len(parts) > 1:
            # Support for chaining methods
            stub = Mocker(_mokit=True)
            assertion.return_value(stub)
            assertion = stub.mock(".".join(parts[1:]))
        self._assertions.append(assertion)
        return assertion

    def _get_original(self, name: str) -> Any:
        """Get original attribute from target object."""
        if hasattr(self._target, "__dict__") and vars(self._target).get(name):
            # This is necessary for static methods to be restored correctly
            return vars(self._target)[name]
        return getattr(self._target, name)

    def _set_mocked_attribute(self, name: str, attr_mock: Any) -> bool:
        """Set mocked attribute on target object and override attributes locally
        when possible.
        """
        local_override = False
        if hasattr(self._target, "__dict__") and not vars(self._target).get(name):
            if isinstance(vars(self._target), dict):
                # Override attribute on a class instance.
                local_override = True
            elif inspect.isclass(self._target):
                # Override attribute on a derived class.
                local_override = True
        setattr(self._target, name, attr_mock)
        return local_override

    def reset(self) -> None:
        while len(self._originals) > 0:
            original, name = self._originals.pop()
            setattr(self._target, name, original)
        while len(self._overrides) > 0:
            name = self._overrides.pop()
            delattr(self._target, name)

    def validate(self) -> None:
        while len(self._assertions) > 0:
            assertion = self._assertions.pop()
            assertion.validate()


class MockerState:
    MOCKERS: Dict[int, Mocker] = {}

    @classmethod
    def add_mocker(cls, mocker_: Mocker, target: Any) -> None:
        cls.MOCKERS[id(target)] = mocker_

    @classmethod
    def get_mocker(cls, target: Any) -> Optional[Mocker]:
        return cls.MOCKERS.get(id(target))

    @classmethod
    def reset(cls) -> None:
        for mocker_ in cls.MOCKERS.values():
            mocker_.reset()

    @classmethod
    def validate(cls) -> None:
        for key in list(cls.MOCKERS):
            mocker_ = cls.MOCKERS.pop(key)
            mocker_.validate()

    @classmethod
    def teardown(cls) -> None:
        cls.reset()
        cls.validate()


def mocker(target: Any = None, **kwargs: Any) -> Mocker:
    mocker_instance = MockerState.get_mocker(target)
    if mocker_instance is None:
        mocker_instance = Mocker(target, _mokit=True)
    for name, value in kwargs.items():
        mocker_instance.mock(name).return_value(value)
    return mocker_instance
