"""Chainmock API implementation."""
# pylint: disable=missing-docstring
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from unittest import mock as umock
from unittest.util import safe_repr

AnyMock = Union[umock.AsyncMock, umock.MagicMock, umock.PropertyMock]
AsyncAndSyncMock = Union[umock.AsyncMock, umock.MagicMock]


class Assert:  # pylint: disable=too-many-public-methods
    def __init__(
        self, parent: Mock, attr_mock: AnyMock, name: str, _internal: bool = False
    ) -> None:
        if not _internal:
            raise RuntimeError(
                "Assert should not be initialized directly. Use mocker function instead."
            )
        self._parent = parent
        self._attr_mock = attr_mock
        self._name = name
        self._assertions: List[Callable[..., None]] = []

    def return_value(self, value: Any) -> Assert:
        """Set the value that will be returned when the mocked attribute is
        called.

        Wrapper for `unittest.mock.Mock.return_value`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.return_value

        Args:
            value: Return value to set to the mocked call.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._attr_mock.return_value = value
        return self

    def side_effect(self, value: Any) -> Assert:
        """Set a side effect that will occur when the mocked attribute is
        called.

        If you pass in a function it will be called with same arguments as the
        mock.

        If you pass in an iterable, it is used to retrieve an iterator which
        must yield a value on every call. This value can either be an exception
        instance to be raised, or a value to be returned from the call to the
        mock.

        Wrapper for `unittest.mock.Mock.side_effect`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.side_effect

        Args:
            value: Function to be called when the mock is called, an iterable or
                an exception (class or instance) to be raised.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._attr_mock.side_effect = value
        return self

    def called_last_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the last call was made with the specified arguments.

        Wrapper for `unittest.mock.Mock.assert_called_with`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_with

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(
            functools.partial(self._attr_mock.assert_called_with, *args, **kwargs)
        )
        return self

    def awaited_last_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the last await was with the specified arguments.

        Wrapper for `unittest.mock.AsyncMock.assert_awaited_with`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited_with

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(
            functools.partial(self._attr_mock.assert_awaited_with, *args, **kwargs)
        )
        return self

    def called_once_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the mock was called exactly once and that call was with
        the specified arguments.

        Wrapper for `unittest.mock.Mock.assert_called_once_with`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_once_with

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(
            functools.partial(self._attr_mock.assert_called_once_with, *args, **kwargs)
        )
        return self

    def awaited_once_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the mock was awaited exactly once with the specified
        arguments.

        Wrapper for `unittest.mock.AsyncMock.assert_awaited_once_with`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited_once_with

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(
            functools.partial(self._attr_mock.assert_awaited_once_with, *args, **kwargs)
        )
        return self

    def any_call_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert the mock has been called with the specified arguments.

        The assert passes if the mock has _ever_ been called with given
        arguments.

        Wrapper for `unittest.mock.Mock.assert_any_call`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_any_call

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._attr_mock.assert_any_call, *args, **kwargs))
        return self

    def any_await_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert the mock has been awaited with the specified arguments.

        The assert passes if the mock has _ever_ been awaited with given
        arguments.

        Wrapper for `unittest.mock.AsyncMock.assert_any_await`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_any_await

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(
            functools.partial(self._attr_mock.assert_any_await, *args, **kwargs)
        )
        return self

    def has_calls(self, calls: Sequence[umock._Call], any_order: bool = False) -> Assert:
        """Assert the mock has been called with the specified calls.

        If `any_order` is True then the calls can be in any order, but they must
        all be matched. If `any_order` is False (default) then the calls must be
        sequential but there can be extra calls before or after the specified
        calls.

        Wrapper for `unittest.mock.Mock.assert_has_calls`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_has_calls

        Args:
            calls: Expected calls. You can import the call type from
                `chainmock.mock.call` or from `unittest.mock.call`.
            any_order: Indicates if the calls must be sequential
                (False, default) or in any order (True).

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(
            functools.partial(self._attr_mock.assert_has_calls, calls, any_order)
        )
        return self

    def has_awaits(self, calls: Sequence[umock._Call], any_order: bool = False) -> Assert:
        """Assert the mock has been awaited with the specified calls.

        If `any_order` is True then the calls can be in any order, but they must
        all be matched. If `any_order` is False (default) then the calls must be
        sequential but there can be extra calls before or after the specified
        calls.

        Wrapper for `unittest.mock.AsyncMock.assert_has_awaits`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_has_awaits

        Args:
            calls: Expected calls. You can import the call type from
                `chainmock.mock.call` or from `unittest.mock.call`.
            any_order: Indicates if the calls must be sequential
                (False, default) or in any order (True).

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(
            functools.partial(self._attr_mock.assert_has_awaits, calls, any_order)
        )
        return self

    def not_called(self) -> Assert:
        """Assert that the mock was never called.

        Wrapper for `unittest.mock.Mock.assert_not_called`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_not_called

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._attr_mock.assert_not_called))
        return self

    def not_awaited(self) -> Assert:
        """Assert that the mock was never awaited.

        Wrapper for `unittest.mock.AsyncMock.assert_not_awaited`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_not_awaited

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._attr_mock.assert_not_awaited))
        return self

    def called(self) -> Assert:
        """Assert that the mock was called at least once.

        Wrapper for `unittest.mock.Mock.assert_called`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._attr_mock.assert_called))
        return self

    def awaited(self) -> Assert:
        """Assert that the mock was awaited at least once.

        Wrapper for `unittest.mock.AsyncMock.assert_awaited`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._attr_mock.assert_awaited))
        return self

    def called_once(self) -> Assert:
        """Assert that the mock was called exactly once.

        Provides similar functionality to `unittest.mock.Mock.assert_called_once`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_once

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._assert_call_count, 1))
        return self

    def awaited_once(self) -> Assert:
        """Assert that the mock was awaited exactly once.

        Provides similar functionality to `unittest.mock.AsyncMock.assert_awaited_once`.

        For more details see:
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited_once

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._assert_await_count, 1))
        return self

    def called_twice(self) -> Assert:
        """Assert that the mock was called exactly twice.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._assert_call_count, 2))
        return self

    def awaited_twice(self) -> Assert:
        """Assert that the mock was awaited exactly twice.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._assert_await_count, 2))
        return self

    def called_times(self, call_count: int) -> Assert:
        """Assert that the mock was called the specified number of times.

        Returns:
            Assert instance so that calls can be chained.
        """
        self._assertions.append(functools.partial(self._assert_call_count, call_count))
        return self

    def awaited_times(self, await_count: int) -> Assert:
        """Assert that the mock was awaited the specified number of times.

        Returns:
            Assert instance so that calls can be chained.
        """
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
            msg = (
                f"Expected '{self._name}' to have been awaited "
                f"{self._format_call_count(await_count)}. "
                f"Awaited {self._format_call_count(self._attr_mock.await_count)}."
                f"{self._awaits_repr()}"
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

    def _awaits_repr(self) -> str:
        """Renders self.mock_awaits as a string.

        Provides similar functionality to `unittest.mock.NonCallableMock._calls_repr`.
        """
        if not self._attr_mock.await_args_list:
            return ""
        return f"\nAwaits: {safe_repr(self._attr_mock.await_args_list)}."

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
    def reset_state(cls) -> None:
        cls.MOCKS = {}

    @classmethod
    def validate_mocks(cls) -> None:
        mocks = cls.MOCKS
        cls.MOCKS = {}
        for mock in mocks.values():
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

    def spy(self, name: str) -> Assert:
        if self._target is None:
            raise RuntimeError("Spying is not available for stubs. Call 'mock' instead.")
        if not name:
            raise ValueError("Attribute name cannot be empty.")
        original = getattr(self._target, name)
        attr_mock = getattr(self._mock, name)
        parameters = tuple(inspect.signature(original).parameters.keys())
        is_class_method = isinstance(inspect.getattr_static(self._target, name), classmethod)
        is_static_method = isinstance(inspect.getattr_static(self._target, name), staticmethod)

        def pass_through(*args: Any, **kwargs: Any) -> Any:
            has_self = len(parameters) > 0 and parameters[0] == "self"
            skip_first = len(args) > len(parameters) and (is_class_method or is_static_method)
            mock_args = list(args)
            if has_self or skip_first:
                mock_args = mock_args[1:]
            attr_mock(*mock_args, **kwargs)
            if skip_first:
                args = tuple(list(args)[1:])
            return original(*args, **kwargs)

        async def async_pass_through(*args: Any, **kwargs: Any) -> Any:
            has_self = len(parameters) > 0 and parameters[0] == "self"
            skip_first = len(args) > len(parameters) and (is_class_method or is_static_method)
            mock_args = list(args)
            if has_self or skip_first:
                mock_args = mock_args[1:]
            await attr_mock(*mock_args, **kwargs)
            if skip_first:
                args = tuple(list(args)[1:])
            return await original(*args, **kwargs)

        if isinstance(attr_mock, umock.AsyncMock):
            patch = umock.patch.object(self._target, name, new_callable=lambda: async_pass_through)
        else:
            patch = umock.patch.object(self._target, name, new_callable=lambda: pass_through)
        patch.start()
        self._object_patches.append(patch)
        assertion = Assert(self, attr_mock, name, _internal=True)
        self._assertions.append(assertion)
        return assertion

    def mock(self, name: str) -> Assert:
        parts = name.split(".")
        name = parts[0]
        parts = parts[1:]
        if not name:
            raise ValueError("Attribute name cannot be empty.")
        if self._target is None:
            assertion = self._stub_attribute(name, parts)
        elif self._patch is not None:
            assertion = self._patch_attribute(name, parts)
        else:
            original = getattr(self._target, name)
            assertion = self._mock_attribute(name, parts, original)
        assertion.return_value(None)
        self._assertions.append(assertion)
        return assertion

    def _stub_attribute(self, name: str, parts: List[str]) -> Assert:
        if name in list(set(dir(Mock)) - set(dir(type))):
            raise ValueError(f"Cannot replace Mock internal attribute {name}")
        attr_mock = getattr(self._mock, name)
        setattr(self, name, attr_mock)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 0:
            # Support for chaining methods
            assertion.return_value(self)
            assertion = self.mock(".".join(parts))
        return assertion

    def _patch_attribute(self, name: str, parts: List[str]) -> Assert:
        if not self._patch_class and self._patch and inspect.isclass(self._patch.temp_original):
            attr_mock: AnyMock = getattr(self._mock(), name)
        else:
            attr_mock = getattr(self._mock, name)
        setattr(self, name, attr_mock)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 0:
            # Support for chaining methods
            stub = Mock(_internal=True)
            assertion.return_value(stub)
            assertion = stub.mock(".".join(parts))
        return assertion

    def _mock_attribute(self, name: str, parts: List[str], original: Any) -> Assert:
        if isinstance(original, property):
            patch = umock.patch.object(self._target, name, new_callable=umock.PropertyMock)
        else:
            patch = umock.patch.object(self._target, name)
        attr_mock = patch.start()
        self._object_patches.append(patch)
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 0:
            # Support for chaining methods
            stub = Mock(_internal=True)
            assertion.return_value(stub)
            assertion = stub.mock(".".join(parts))
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
