"""Chainmock API implementation."""
# pylint: disable=missing-docstring
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
from unittest import mock as umock

AnyMock = Union[umock.AsyncMock, umock.MagicMock, umock.PropertyMock]
AsyncAndSyncMock = Union[umock.AsyncMock, umock.MagicMock]


class Assert:  # pylint: disable=too-many-public-methods
    def __init__(
        self, parent: Mock, attr_mock: AnyMock, name: str, _internal: bool = False
    ) -> None:
        if not _internal:
            raise RuntimeError("Assert should not be initialized directly.")
        self._parent = parent
        self._attr_mock = attr_mock
        self._name = name
        self._assertions: List[Callable[..., None]] = []

    def return_value(self, value: Any) -> Assert:
        self._attr_mock.return_value = value
        return self

    def side_effect(self, value: Any) -> Assert:
        self._attr_mock.side_effect = value
        return self

    def called_with(self, *args: Any, **kwargs: Any) -> Assert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_called_with, *args, **kwargs)
        )
        return self

    def awaited_with(self, *args: Any, **kwargs: Any) -> Assert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_awaited_with, *args, **kwargs)
        )
        return self

    def called_once_with(self, *args: Any, **kwargs: Any) -> Assert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_called_once_with, *args, **kwargs)
        )
        return self

    def awaited_once_with(self, *args: Any, **kwargs: Any) -> Assert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_awaited_once_with, *args, **kwargs)
        )
        return self

    def any_call(self, *args: Any, **kwargs: Any) -> Assert:
        self._assertions.append(functools.partial(self._attr_mock.assert_any_call, *args, **kwargs))
        return self

    def any_await(self, *args: Any, **kwargs: Any) -> Assert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_any_await, *args, **kwargs)
        )
        return self

    def has_calls(self, calls: Sequence[umock._Call], any_order: bool = False) -> Assert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_has_calls, calls, any_order)
        )
        return self

    def has_awaits(self, calls: Sequence[umock._Call], any_order: bool = False) -> Assert:
        self._assertions.append(
            functools.partial(self._attr_mock.assert_has_awaits, calls, any_order)
        )
        return self

    def not_called(self) -> Assert:
        self._assertions.append(functools.partial(self._attr_mock.assert_not_called))
        return self

    def not_awaited(self) -> Assert:
        self._assertions.append(functools.partial(self._attr_mock.assert_not_awaited))
        return self

    def called(self) -> Assert:
        self._assertions.append(functools.partial(self._attr_mock.assert_called))
        return self

    def awaited(self) -> Assert:
        self._assertions.append(functools.partial(self._attr_mock.assert_awaited))
        return self

    def called_once(self) -> Assert:
        self._assertions.append(functools.partial(self._assert_call_count, 1))
        return self

    def awaited_once(self) -> Assert:
        self._assertions.append(functools.partial(self._assert_await_count, 1))
        return self

    def called_twice(self) -> Assert:
        self._assertions.append(functools.partial(self._assert_call_count, 2))
        return self

    def awaited_twice(self) -> Assert:
        self._assertions.append(functools.partial(self._assert_await_count, 2))
        return self

    def called_times(self, call_count: int) -> Assert:
        self._assertions.append(functools.partial(self._assert_call_count, call_count))
        return self

    def awaited_times(self, await_count: int) -> Assert:
        self._assertions.append(functools.partial(self._assert_await_count, await_count))
        return self

    def self(self) -> Mock:
        return self._parent

    def _validate(self) -> None:
        while len(self._assertions) > 0:
            assertion = self._assertions.pop()
            assertion()

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
            msg = (
                f"Expected '{self._name}' to have been called "
                f"{self._format_call_count(call_count)}. "
                f"Called {self._format_call_count(self._attr_mock.call_count)}."
                f"{self._attr_mock._calls_repr()}"  # pylint:disable=protected-access
            )
            raise AssertionError(msg)

    @staticmethod
    def _format_call_count(call_count: int) -> str:
        if call_count == 1:
            return "once"
        if call_count == 2:
            return "twice"
        return f"{call_count} times"


class State:
    MOCKS: Dict[Union[int, str], Mock] = {}

    @classmethod
    def get_or_create_mock(cls, target: Any) -> Mock:
        key: Union[int, str]
        if isinstance(target, str):
            key = target
        else:
            key = id(target)
        mock = cls.MOCKS.get(key)
        if mock is None:
            patch = None
            if isinstance(target, str):
                patch = umock.patch(target, spec=True)
            mock = Mock(target, patch, _internal=True)
            cls.MOCKS[key] = mock
        return mock

    @classmethod
    def reset_mocks(cls) -> None:
        for mock in cls.MOCKS.values():
            mock._reset()  # pylint: disable=protected-access

    @classmethod
    def validate_mocks(cls) -> None:
        for key in list(cls.MOCKS):
            mock = cls.MOCKS.pop(key)
            mock._validate()  # pylint: disable=protected-access

    @classmethod
    def teardown(cls) -> None:
        cls.reset_mocks()
        cls.validate_mocks()


class Mock:
    def __init__(
        self,
        target: Any = None,
        patch: Optional[
            umock._patch[AsyncAndSyncMock]  # pylint: disable=unsubscriptable-object
        ] = None,
        *,
        _internal: bool = False,
    ) -> None:
        if not _internal:
            raise RuntimeError(
                "Mock should not be initialized directly. Use mocker function instead."
            )
        self._target = target
        self._patch = patch
        self._mock = patch.start() if patch else umock.MagicMock(spec=target)
        self._assertions: List[Assert] = []
        self._originals: List[Tuple[Any, str]] = []
        self._overrides: List[str] = []

    def mock(self, name: str) -> Assert:
        parts = name.split(".")
        if not parts:
            raise ValueError("Method name cannot be empty")
        name = parts[0]
        attr_mock: AnyMock = getattr(self._mock, name)
        if self._target is None:
            assertion = self._stub_attribute(name, attr_mock, parts)
        elif self._patch is not None:
            assertion = self._patch_attribute(name, attr_mock, parts)
        else:
            assertion = self._mock_attribute(name, attr_mock, parts)
        assertion.return_value(None)
        self._assertions.append(assertion)
        return assertion

    def _stub_attribute(self, name: str, attr_mock: AnyMock, parts: List[str]) -> Assert:
        if name in list(set(dir(Mock)) - set(dir(type))):
            raise ValueError(f"Cannot replace Mock internal attribute {name}")
        setattr(self, name, attr_mock)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 1:
            # Support for chaining methods
            assertion.return_value(self)
            assertion = self.mock(".".join(parts[1:]))
        return assertion

    def _patch_attribute(self, name: str, attr_mock: AnyMock, parts: List[str]) -> Assert:
        setattr(self, name, attr_mock)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 1:
            # Support for chaining methods
            assertion.return_value(self)
            assertion = self.mock(".".join(parts[1:]))
        return assertion

    def _mock_attribute(self, name: str, attr_mock: AnyMock, parts: List[str]) -> Assert:
        original = self._get_original(name)
        if isinstance(original, property):
            attr_mock = umock.PropertyMock()
        local_override = self._set_mocked_attribute(name, attr_mock)
        if local_override:
            self._overrides.append(name)
        elif name not in self._overrides and name not in [name for _, name in self._originals]:
            self._originals.append((original, name))
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 1:
            # Support for chaining methods
            stub = Mock(_internal=True)
            assertion.return_value(stub)
            assertion = stub.mock(".".join(parts[1:]))
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

    def _reset(self) -> None:
        while len(self._originals) > 0:
            original, name = self._originals.pop()
            setattr(self._target, name, original)
        while len(self._overrides) > 0:
            name = self._overrides.pop()
            delattr(self._target, name)
        if self._patch is not None:
            self._patch.stop()

    def _validate(self) -> None:
        while len(self._assertions) > 0:
            assertion = self._assertions.pop()
            assertion._validate()  # pylint: disable=protected-access


def mocker(target: Any = None, **kwargs: Any) -> Mock:
    mock = State.get_or_create_mock(target)
    for name, value in kwargs.items():
        mock.mock(name).return_value(value)
    return mock
