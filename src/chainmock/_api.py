"""Chainmock API implementation."""
# pylint: disable=missing-docstring
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
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
    def get_or_create_mock(
        cls,
        target: Optional[Any],
        *,
        spec: Optional[Any] = None,
        patch_class: bool = False,
    ) -> Mock:
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
            mock = Mock(target, patch=patch, spec=spec, patch_class=patch_class, _internal=True)
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
        target: Optional[Any] = None,
        *,
        patch: Optional[
            umock._patch[AsyncAndSyncMock]  # pylint: disable=unsubscriptable-object
        ] = None,
        spec: Optional[Any] = None,
        patch_class: bool = False,
        _internal: bool = False,
    ) -> None:
        if not _internal:
            raise RuntimeError(
                "Mock should not be initialized directly. Use mocker function instead."
            )
        self._target = target
        self._spec = spec
        self._patch = patch
        self._mock = (
            patch.start() if patch else umock.MagicMock(spec=spec if spec is not None else target)
        )
        self._assertions: List[Assert] = []
        self._object_patches: List[
            umock._patch[AsyncAndSyncMock]  # pylint: disable=unsubscriptable-object
        ] = []
        self._patch_class: bool = patch_class

    def mock(self, name: str) -> Assert:
        parts = name.split(".")
        if not parts:
            raise ValueError("Method name cannot be empty")
        name = parts[0]
        if self._target is None:
            assertion = self._stub_attribute(name, parts)
        elif self._patch is not None:
            assertion = self._patch_attribute(name, parts)
        else:
            assertion = self._mock_attribute(name, parts)
        assertion.return_value(None)
        self._assertions.append(assertion)
        return assertion

    def _stub_attribute(self, name: str, parts: List[str]) -> Assert:
        if name in list(set(dir(Mock)) - set(dir(type))):
            raise ValueError(f"Cannot replace Mock internal attribute {name}")
        attr_mock = getattr(self._mock, name)
        setattr(self, name, attr_mock)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 1:
            # Support for chaining methods
            assertion.return_value(self)
            assertion = self.mock(".".join(parts[1:]))
        return assertion

    def _patch_attribute(self, name: str, parts: List[str]) -> Assert:
        if not self._patch_class and self._patch and inspect.isclass(self._patch.temp_original):
            attr_mock: AnyMock = getattr(self._mock(), name)
        else:
            attr_mock = getattr(self._mock, name)
        setattr(self, name, attr_mock)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 1:
            # Support for chaining methods
            assertion.return_value(self)
            assertion = self.mock(".".join(parts[1:]))
        return assertion

    def _mock_attribute(self, name: str, parts: List[str]) -> Assert:
        original = getattr(self._target, name)
        if isinstance(original, property):
            patch = umock.patch.object(self._target, name, new_callable=umock.PropertyMock)
        else:
            patch = umock.patch.object(self._target, name)
        attr_mock = patch.start()
        self._object_patches.append(patch)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 1:
            # Support for chaining methods
            stub = Mock(_internal=True)
            assertion.return_value(stub)
            assertion = stub.mock(".".join(parts[1:]))
        return assertion

    def _reset(self) -> None:
        while len(self._object_patches) > 0:
            patch = self._object_patches.pop()
            patch.stop()
        if self._patch is not None:
            self._patch.stop()

    def _validate(self) -> None:
        while len(self._assertions) > 0:
            assertion = self._assertions.pop()
            assertion._validate()  # pylint: disable=protected-access


def mocker(
    target: Optional[Any] = None,
    *,
    spec: Optional[Any] = None,
    patch_class: bool = False,
    **kwargs: Any,
) -> Mock:
    mock = State.get_or_create_mock(target, spec=spec, patch_class=patch_class)
    for name, value in kwargs.items():
        mock.mock(name).return_value(value)
    return mock
