"""Chainmock API implementation."""
# pylint: disable=too-many-lines
from __future__ import annotations

import functools
import inspect
import itertools
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Type, Union
from unittest import mock as umock
from unittest.util import safe_repr

AnyMock = Union[umock.AsyncMock, umock.MagicMock, umock.PropertyMock]
AsyncAndSyncMock = Union[umock.AsyncMock, umock.MagicMock]


class Assert:
    """Assert allows creation of assertions for mocks.

    The created assertions are automatically validated at the end of a test.

    Assert should not be initialized directly. Use mocker function instead.
    """

    def __init__(
        self,
        parent: Mock,
        attr_mock: AnyMock,
        name: str,
        *,
        kind: Literal["spy", "mock"] = "mock",
        patch: Optional[umock._patch[Any]] = None,  # pylint: disable=unsubscriptable-object
        _internal: bool = False,
    ) -> None:
        if not _internal:
            raise RuntimeError(
                "Assert should not be initialized directly. Use mocker function instead."
            )
        self.__parent = parent
        self.__attr_mock = attr_mock
        self.__name = name
        self.__assertions: List[Callable[..., None]] = []
        self.__patch = patch
        self._kind = kind

    def get_mock(self) -> AnyMock:
        """Return the unittest mock associated with this Assert object.

        This method can be used if you want to access the underlying unittest
        mock directly. Normally, there should not be a need for this, but you can
        use this method if you prefer to call the assertion methods directly on
        the unittest mock instead of using chainmock's methods.

        One difference between calling assertion methods on the unittest mock
        and chainmock is that unittest mock validates the assertions right
        away whereas chainmock verifies the assertions after the test execution
        during test teardown. Therefore, unittest mock allows making assertions
        before the test execution. If you are not sure what this means, see the
        examples section.

        Examples:
            Mock the `add_tea` method and call assertions directly on unittest
            mock:

            >>> teapot = Teapot()
            >>> mock = mocker(teapot).mock("add_tea").get_mock()
            >>> # Using get_mock allows making assertions before test teardown
            >>> mock.assert_not_called()
            >>> teapot.add_tea("green")
            >>> mock.assert_called_once_with("green")

            The above code can be written without calling `get_mock` as follows:

            >>> teapot = Teapot()
            >>> mocker(teapot).mock("add_tea").called_once_with("green")
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("green")

        Returns:
            Python unittest mock (`AsyncMock`, `MagicMock`, or `PropertyMock`).
        """
        return self.__attr_mock

    def return_value(self, value: Any) -> Assert:
        """Set the value that will be returned when the mocked attribute is
        called.

        Wrapper for `unittest.mock.Mock.return_value`.

        For more details see:
        [unittest.mock.Mock.return_value](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.return_value)

        Examples:
            Mock the return value of method `brew`:

            >>> mocker(Teapot).mock("brew").return_value("mocked")
            <chainmock._api.Assert object at ...>
            >>> Teapot().brew()
            'mocked'

        Args:
            value: Return value to set to the mocked call.

        Returns:
            Assert instance so that calls can be chained.
        """
        if isinstance(self.__attr_mock, umock.NonCallableMagicMock) and self.__patch is not None:
            # Support mocking module attributes/variables
            self.__patch.stop()
            self.__patch.new = value
            self.__patch.start()
            return self
        self.__attr_mock.return_value = value
        return self

    def side_effect(self, value: Any) -> Assert:
        """Set a side effect that will occur when the mocked attribute is
        called.

        Side effect can be a function to call, an iterable or an exception
        (class or instance) to be raised. If you pass in a function it will be
        called with same arguments as the mock.

        If you pass in an iterable, it is used to retrieve an iterator which
        must yield a value on every call. This value can either be an exception
        instance to be raised, or a value to be returned from the call to the
        mock.

        Wrapper for `unittest.mock.Mock.side_effect`.

        For more details see:
        [unittest.mock.Mock.side_effect](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.side_effect)

        Examples:
            Raise an exception when the method `brew` is called:

            >>> mocker(Teapot).mock("brew").side_effect(Exception("No tea!"))
            <chainmock._api.Assert object at ...>
            >>> Teapot().brew()
            Traceback (most recent call last):
              ...
            Exception: No tea!

            Replace method `fill` with another function:

            >>> mocker(teapot).mock("fill").side_effect(lambda x: x + 1)
            <chainmock._api.Assert object at ...>
            >>> teapot.fill(1)
            2

            Use a list to return a sequence of values:

            >>> mocker(teapot).mock("pour").side_effect([2, 1, Exception("empty")])
            <chainmock._api.Assert object at ...>
            >>> teapot.pour()
            2
            >>> teapot.pour()
            1
            >>> teapot.pour()
            Traceback (most recent call last):
              ...
            Exception: empty

        Args:
            value: Function to be called when the mock is called, an iterable or
                an exception (class or instance) to be raised.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__attr_mock.side_effect = value
        return self

    def called_last_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the _most recent call_ was made with the specified arguments.

        Wrapper for `unittest.mock.Mock.assert_called_with`.

        For more details see:
        [unittest.mock.Mock.assert_called_with](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_with)

        Examples:
            >>> mocker(Teapot).mock("add_tea").called_last_with("green", loose=True)
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("green", loose=True)

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_called_with, *args, **kwargs)
        )
        return self

    def awaited_last_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the _most recent await_ was with the specified arguments.

        Wrapper for `unittest.mock.AsyncMock.assert_awaited_with`.

        For more details see:
        [unittest.mock.AsyncMock.assert_awaited_with](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited_with)

        Examples:
            >>> mocker(teapot).mock("timer").awaited_last_with(minutes=10)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(minutes=10))

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_awaited_with, *args, **kwargs)
        )
        return self

    def match_args_last_call(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the _most recent call_ has _at least_ the specified
        arguments.

        The assert passes if the last call has at least the given positional or
        keyword arguments. This can be useful when you want to match just one
        specific argument and do not care about the rest.

        If you want all of the arguments to match, use `called_last_with` method
        instead.

        Examples:
            Below assertion passes because `add_tea` was called with positional
            argument `black`. Keyword argument `loose` is ignored.

            >>> mocker(Teapot).mock("add_tea").match_args_last_call("black")
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("black", loose=False)

            Below assertion passes because `add_tea` was called with keyword
            argument `loose=True`. Positional argument is ignored.

            >>> mocker(teapot).mock("add_tea").match_args_last_call(loose=True)
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("oolong", loose=True)

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_match_call_args, "last", *args, **kwargs)
        )
        return self

    def match_args_last_await(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the _most recent await_ has _at least_ the specified
        arguments.

        The assert passes if the last await has at least the given positional or
        keyword arguments. This can be useful when you want to match just one
        specific argument and do not care about the rest.

        If you want all of the arguments to match, use `awaited_last_with` method
        instead.

        Examples:
            Below assertion passes because `timer` was awaited with positional
            argument `5`. Keyword argument `seconds` is ignored.

            >>> mocker(Teapot).mock("timer").match_args_any_await(5)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(Teapot().timer(5, seconds=15))

            Below assertion passes because `timer` was awaited with keyword
            argument `seconds=30`. Positional argument is ignored.

            >>> mocker(teapot).mock("timer").match_args_any_await(seconds=30)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(1, seconds=30))

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_match_await_args, "last", *args, **kwargs)
        )
        return self

    def called_once_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the mock was called exactly once and that call was with
        the specified arguments.

        Wrapper for `unittest.mock.Mock.assert_called_once_with`.

        For more details see:
        [unittest.mock.Mock.assert_called_once_with](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_once_with)

        Examples:
            >>> mocker(Teapot).mock("add_tea").called_once_with("puehr")
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("puehr")

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_called_once_with, *args, **kwargs)
        )
        return self

    def awaited_once_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the mock was awaited exactly once with the specified
        arguments.

        Wrapper for `unittest.mock.AsyncMock.assert_awaited_once_with`.

        For more details see:
        [unittest.mock.AsyncMock.assert_awaited_once_with](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited_once_with)

        Examples:
            >>> mocker(teapot).mock("timer").called_once_with(5)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(5))

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_awaited_once_with, *args, **kwargs)
        )
        return self

    def any_call_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the mock has been called with the specified arguments.

        The assert passes if the mock has _ever_ been called with given
        arguments.

        Wrapper for `unittest.mock.Mock.assert_any_call`.

        For more details see:
        [unittest.mock.Mock.assert_any_call](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_any_call)

        Examples:
            >>> mocker(Teapot).mock("add_tea").any_call_with("black")
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("oolong")
            >>> Teapot().add_tea("black")

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_any_call, *args, **kwargs)
        )
        return self

    def any_await_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that the mock has been awaited with the specified arguments.

        The assert passes if the mock has _ever_ been awaited with given
        arguments.

        Wrapper for `unittest.mock.AsyncMock.assert_any_await`.

        For more details see:
        [unittest.mock.AsyncMock.assert_any_await](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_any_await)

        Examples:
            >>> mocker(teapot).mock("timer").any_call_with(5)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(5))
            >>> asyncio.run(teapot.timer(3))

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_any_await, *args, **kwargs)
        )
        return self

    def all_calls_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that _all_ calls have the specified arguments.

        The assert passes if _all_ calls have been made with the given
        arguments.

        Examples:
            >>> mocker(Teapot).mock("add_tea").all_calls_with("black")
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("black")
            >>> Teapot().add_tea("black")

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_all_calls_with, *args, **kwargs))
        return self

    def all_awaits_with(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that _all_ awaits have the specified arguments.

        The assert passes if _all_ awaits have been made with the given
        arguments.

        Examples:
            >>> mocker(teapot).mock("timer").all_calls_with(5)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(5))
            >>> asyncio.run(teapot.timer(5))

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_all_awaits_with, *args, **kwargs))
        return self

    def match_args_any_call(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that any call has _at least_ the specified arguments.

        The assert passes if any call has at least the given positional or
        keyword arguments. This can be useful when you want to match just one
        specific argument and do not care about the rest.

        If you want all of the arguments to match, use `any_call_with` method
        instead.

        Examples:
            Below assertion passes because `add_tea` was called with positional
            argument `black`. Keyword argument `loose` is ignored.

            >>> mocker(Teapot).mock("add_tea").match_args_any_call("black")
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("black", loose=False)

            Below assertion passes because `add_tea` was called with keyword
            argument `loose=True`. Positional argument is ignored.

            >>> mocker(Teapot).mock("add_tea").match_args_any_call(loose=True)
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("oolong", loose=True)

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_match_call_args, "any", *args, **kwargs)
        )
        return self

    def match_args_any_await(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that any await has _at least_ the specified arguments.

        The assert passes if any await has at least the given positional or
        keyword arguments. This can be useful when you want to match just one
        specific argument and do not care about the rest.

        If you want all of the arguments to match, use `any_await_with` method
        instead.

        Examples:
            Below assertion passes because `timer` was awaited with positional
            argument `5`. Keyword argument `seconds` is ignored.

            >>> mocker(Teapot).mock("timer").match_args_any_await(5)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(Teapot().timer(5, seconds=15))

            Below assertion passes because `timer` was awaited with keyword
            argument `seconds=30`. Positional argument is ignored.

            >>> mocker(Teapot).mock("timer").match_args_any_await(seconds=30)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(Teapot().timer(1, seconds=30))

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_match_await_args, "any", *args, **kwargs)
        )
        return self

    def match_args_all_calls(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that _all_ calls have _at least_ the specified arguments.

        The assert passes if all calls have at least the given positional or
        keyword arguments. This can be useful when you want to match just one
        specific argument and do not care about the rest.

        If you want all of the arguments to match, use `all_calls_with` method
        instead.

        Examples:
            Below assertion passes because all calls to `add_tea` have
            positional argument `oolong`. Keyword arguments are ignored.

            >>> teapot = Teapot()
            >>> mocker(teapot).mock("add_tea").match_args_all_calls("oolong")
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("oolong", loose=False)
            >>> teapot.add_tea("oolong", loose=True)
            >>> teapot.add_tea("oolong")

            Below assertion passes because all calls to `add_tea` have keyword
            argument `loose=True`. Positional arguments are ignored.

            >>> teapot = Teapot()
            >>> mocker(teapot).mock("add_tea").match_args_all_calls(loose=True)
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("oolong", loose=True)
            >>> teapot.add_tea("black", loose=True)
            >>> teapot.add_tea("green", loose=True)

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_match_call_args, "all", *args, **kwargs)
        )
        return self

    def match_args_all_awaits(self, *args: Any, **kwargs: Any) -> Assert:
        """Assert that _all_ awaits have _at least_ the specified arguments.

        The assert passes if all awaits have at least the given positional or
        keyword arguments. This can be useful when you want to match just one
        specific argument and do not care about the rest.

        If you want all of the arguments to match, use `all_awaits_with` method
        instead.

        Examples:
            Below assertion passes because all awaits to `timer` have positional
            argument `5`. Keyword arguments `seconds` are ignored.

            >>> teapot = Teapot()
            >>> mocker(teapot).mock("timer").match_args_all_awaits(5)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(5, seconds=15))
            >>> asyncio.run(teapot.timer(5, seconds=30))
            >>> asyncio.run(teapot.timer(5))

            Below assertion passes because all awaits to `timer` have keyword
            argument `seconds=30`. Positional arguments are ignored.

            >>> teapot = Teapot()
            >>> mocker(teapot).mock("timer").match_args_all_awaits(seconds=30)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(1, seconds=30))
            >>> asyncio.run(teapot.timer(5, seconds=30))
            >>> asyncio.run(teapot.timer(10, seconds=30))

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_match_await_args, "all", *args, **kwargs)
        )
        return self

    def has_calls(self, calls: Sequence[umock._Call], any_order: bool = False) -> Assert:
        """Assert that the mock has been called with the specified calls.

        If `any_order` is True then the calls can be in any order, but they must
        all be matched. If `any_order` is False (default) then the calls must be
        sequential but there can be extra calls before or after the specified
        calls.

        Wrapper for `unittest.mock.Mock.assert_has_calls`.

        For more details see:
        [unittest.mock.Mock.assert_has_calls](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_has_calls)

        Examples:
            >>> from chainmock.mock import call
            >>> mocker(Teapot).mock("add_tea").has_calls([call("oolong"), call("black")])
            <chainmock._api.Assert object at ...>
            >>> Teapot().add_tea("oolong")
            >>> Teapot().add_tea("black")

        Args:
            calls: Expected calls. You can import the call type from
                `chainmock.mock.call` or from `unittest.mock.call`.
            any_order: Indicates if the calls must be sequential
                (False, default) or in any order (True).

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_has_calls, calls, any_order)
        )
        return self

    def has_awaits(self, calls: Sequence[umock._Call], any_order: bool = False) -> Assert:
        """Assert that the mock has been awaited with the specified calls.

        If `any_order` is True then the calls can be in any order, but they must
        all be matched. If `any_order` is False (default) then the calls must be
        sequential but there can be extra calls before or after the specified
        calls.

        Wrapper for `unittest.mock.AsyncMock.assert_has_awaits`.

        For more details see:
        [unittest.mock.AsyncMock.assert_has_awaits](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_has_awaits)

        Examples:
            >>> from chainmock.mock import call
            >>> mocker(teapot).mock("timer").has_awaits([call(5), call(3)])
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(5))
            >>> asyncio.run(teapot.timer(3))

        Args:
            calls: Expected calls. You can import the call type from
                `chainmock.mock.call` or from `unittest.mock.call`.
            any_order: Indicates if the calls must be sequential
                (False, default) or in any order (True).

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self.__attr_mock.assert_has_awaits, calls, any_order)
        )
        return self

    def not_called(self) -> Assert:
        """Assert that the mock was never called.

        Wrapper for `unittest.mock.Mock.assert_not_called`.

        For more details see:
        [unittest.mock.Mock.assert_not_called](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_not_called)

        Examples:
            >>> mocker(Teapot).mock("pour").not_called()
            <chainmock._api.Assert object at ...>

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self.__attr_mock.assert_not_called))
        return self

    def not_awaited(self) -> Assert:
        """Assert that the mock was never awaited.

        Wrapper for `unittest.mock.AsyncMock.assert_not_awaited`.

        For more details see:
        [unittest.mock.AsyncMock.assert_not_awaited](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_not_awaited)

        Examples:
            >>> mocker(Teapot).mock("timer").not_awaited()
            <chainmock._api.Assert object at ...>

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self.__attr_mock.assert_not_awaited))
        return self

    def called(self) -> Assert:
        """Assert that the mock was called at least once.

        Wrapper for `unittest.mock.Mock.assert_called`.

        For more details see:
        [unittest.mock.Mock.assert_called](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called)

        Examples:
            >>> mocker(Teapot).mock("pour").called()
            <chainmock._api.Assert object at ...>
            >>> Teapot().pour()

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self.__attr_mock.assert_called))
        return self

    def awaited(self) -> Assert:
        """Assert that the mock was awaited at least once.

        Wrapper for `unittest.mock.AsyncMock.assert_awaited`.

        For more details see:
        [unittest.mock.AsyncMock.assert_awaited](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited)

        Examples:
            >>> mocker(Teapot).mock("timer").awaited()
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(Teapot().timer())

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self.__attr_mock.assert_awaited))
        return self

    def called_once(self) -> Assert:
        """Assert that the mock was called exactly once.

        Provides similar functionality to `unittest.mock.Mock.assert_called_once`.

        For more details see:
        [unittest.mock.Mock.assert_called_once](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called_once)

        Examples:
            >>> mocker(Teapot).mock("boil").called_once()
            <chainmock._api.Assert object at ...>
            >>> Teapot().boil()

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_call_count, 1))
        return self

    def awaited_once(self) -> Assert:
        """Assert that the mock was awaited exactly once.

        Provides similar functionality to `unittest.mock.AsyncMock.assert_awaited_once`.

        For more details see:
        [unittest.mock.AsyncMock.assert_awaited_once](
        https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock.assert_awaited_once)

        Examples:
            >>> mocker(Teapot).mock("open").awaited_once()
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(Teapot().open())

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_await_count, 1))
        return self

    def called_twice(self) -> Assert:
        """Assert that the mock was called exactly twice.

        Examples:
            >>> mocker(teapot).mock("pour").called_twice()
            <chainmock._api.Assert object at ...>
            >>> teapot.pour()
            >>> teapot.pour()

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_call_count, 2))
        return self

    def awaited_twice(self) -> Assert:
        """Assert that the mock was awaited exactly twice.

        Examples:
            >>> mocker(teapot).mock("timer").awaited_twice()
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.timer(1))
            >>> asyncio.run(teapot.timer(2))

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_await_count, 2))
        return self

    def call_count(self, call_count: int) -> Assert:
        """Assert that the mock was called the specified number of times.

        Examples:
            >>> mocker(teapot).mock("pour").call_count(3)
            <chainmock._api.Assert object at ...>
            >>> teapot.pour()
            >>> teapot.pour()
            >>> teapot.pour()

        Args:
            call_count: Expected call count.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_call_count, call_count))
        return self

    def await_count(self, await_count: int) -> Assert:
        """Assert that the mock was awaited the specified number of times.

        Examples:
            >>> mocker(teapot).mock("open").await_count(3)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.open())
            >>> asyncio.run(teapot.open())
            >>> asyncio.run(teapot.open())

        Args:
            await_count: Expected await count.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_await_count, await_count))
        return self

    def call_count_at_least(self, call_count: int) -> Assert:
        """Assert that the mock was called _at least_ the specified number of times.

        Examples:
            Assert that the method `pour` was called at least once:

            >>> mocker(teapot).mock("pour").call_count_at_least(1)
            <chainmock._api.Assert object at ...>
            >>> teapot.pour()
            >>> teapot.pour()

            Assert that the method `boil` was called at least once but not more
            than twice:

            >>> mocker(teapot).mock("boil").call_count_at_least(1).call_count_at_most(2)
            <chainmock._api.Assert object at ...>
            >>> teapot.boil()
            >>> teapot.boil()

        Args:
            call_count: Expected call count.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_call_count, call_count, "at least"))
        return self

    def await_count_at_least(self, await_count: int) -> Assert:
        """Assert that the mock was awaited _at least_ the specified number of times.

        Examples:
            Assert that the method `open` was awaited at least once:

            >>> mocker(teapot).mock("open").await_count_at_least(1)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.open())
            >>> asyncio.run(teapot.open())

            Assert that the method `close` was awaited at least once but not more
            than twice:

            >>> mocker(teapot).mock("close").await_count_at_least(1).await_count_at_most(2)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.close())
            >>> asyncio.run(teapot.close())

        Args:
            await_count: Expected await count.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_await_count, await_count, "at least")
        )
        return self

    def call_count_at_most(self, call_count: int) -> Assert:
        """Assert that the mock was called _at most_ the specified number of times.

        Examples:
            Assert that the method `pour` was called at most twice:

            >>> mocker(teapot).mock("pour").call_count_at_most(2)
            <chainmock._api.Assert object at ...>
            >>> teapot.pour()
            >>> teapot.pour()

            Assert that the method `boil` was called at most twice and at least
            once:

            >>> mocker(teapot).mock("boil").call_count_at_most(2).call_count_at_least(1)
            <chainmock._api.Assert object at ...>
            >>> teapot.boil()
            >>> teapot.boil()

        Args:
            call_count: Expected call count.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(functools.partial(self._assert_call_count, call_count, "at most"))
        return self

    def await_count_at_most(self, await_count: int) -> Assert:
        """Assert that the mock was awaited _at most_ the specified number of times.

        Examples:
            Assert that the method `open` was awaited at most twice:

            >>> mocker(teapot).mock("open").await_count_at_most(2)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.open())
            >>> asyncio.run(teapot.open())

            Assert that the method `close` was awaited at most twice and at least
            once:

            >>> mocker(teapot).mock("close").await_count_at_most(2).await_count_at_least(1)
            <chainmock._api.Assert object at ...>
            >>> asyncio.run(teapot.close())
            >>> asyncio.run(teapot.close())

        Args:
            await_count: Expected await count.

        Returns:
            Assert instance so that calls can be chained.
        """
        self.__assertions.append(
            functools.partial(self._assert_await_count, await_count, "at most")
        )
        return self

    def self(self) -> Mock:
        """Return the mock associated with this assertion.

        Examples:
            Use `self` to return mock and add more assertions:

            >>> teapot = Teapot()
            >>> mocked = mocker(teapot).mock("fill").called_once().self()
            >>> mocked.mock("boil").called_once()
            <chainmock._api.Assert object at ...>
            >>> teapot.fill()
            >>> teapot.boil()

            Without `self` the above example can be written also like this:

            >>> teapot = Teapot()
            >>> mocked = mocker(teapot)
            >>> mocked.mock("fill").called_once()
            <chainmock._api.Assert object at ...>
            >>> mocked.mock("boil").called_once()
            <chainmock._api.Assert object at ...>
            >>> teapot.fill()
            >>> teapot.boil()

        Returns:
            Mock instance associated with this assertion.
        """
        return self.__parent

    def _assert_call_count(
        self, call_count: int, modifier: Optional[Literal["at least", "at most"]] = None
    ) -> None:
        if modifier is None and self.__attr_mock.call_count == call_count:
            return
        if modifier == "at least" and self.__attr_mock.call_count >= call_count:
            return
        if modifier == "at most" and self.__attr_mock.call_count <= call_count:
            return
        modifier_str = f"{modifier} " if modifier else ""
        msg = (
            f"Expected '{self.__name}' to have been called {modifier_str}"  # pylint:disable=protected-access
            f"{self._format_call_count(call_count)}. "
            f"Called {self._format_call_count(self.__attr_mock.call_count)}."
            f"{self.__attr_mock._calls_repr()}"
        )
        raise AssertionError(msg)

    def _assert_await_count(
        self, await_count: int, modifier: Optional[Literal["at least", "at most"]] = None
    ) -> None:
        if modifier is None and self.__attr_mock.await_count == await_count:
            return
        if modifier == "at least" and self.__attr_mock.await_count >= await_count:
            return
        if modifier == "at most" and self.__attr_mock.await_count <= await_count:
            return
        modifier_str = f"{modifier} " if modifier else ""
        msg = (
            f"Expected '{self.__name}' to have been awaited {modifier_str}"
            f"{self._format_call_count(await_count)}. "
            f"Awaited {self._format_call_count(self.__attr_mock.await_count)}."
            f"{self._awaits_repr()}"
        )
        raise AssertionError(msg)

    def _assert_all_calls_with(self, *args: Any, **kwargs: Any) -> None:
        if not self._all_args_match(self.__attr_mock.call_args_list, *args, **kwargs):
            msg = (
                f"All calls have not been made with the given arguments:\n"  # pylint:disable=protected-access
                f"{self._args_repr(*args, **kwargs)}"
                f"{self.__attr_mock._calls_repr()}"
            )
            raise AssertionError(msg)

    def _assert_all_awaits_with(self, *args: Any, **kwargs: Any) -> None:
        if not self._all_args_match(self.__attr_mock.await_args_list, *args, **kwargs):
            msg = (
                f"All awaits have not been made with the given arguments:\n"
                f"{self._args_repr(*args, **kwargs)}"
                f"{self._awaits_repr()}"
            )
            raise AssertionError(msg)

    @staticmethod
    def _all_args_match(args_list: umock._CallList, *args: Any, **kwargs: Any) -> bool:
        expected_call = umock.call(*args, **kwargs)
        for call in args_list:
            if call != expected_call:
                return False
        return True

    def _assert_match_call_args(  # pylint: disable=too-many-branches
        self, modifier: Literal["all", "any", "last"], *args: Any, **kwargs: Any
    ) -> None:
        if not self._assert_match_args(self.__attr_mock.call_args_list, modifier, *args, **kwargs):
            if modifier == "last":
                msg = "Last call does not include arguments"
            elif modifier == "all":
                msg = "All calls do not contain the given arguments"
            else:
                msg = "No call includes arguments"
            msg = (
                f"{msg}:\n"  # pylint:disable=protected-access
                f"{self._args_repr(*args, **kwargs)}"
                f"{self.__attr_mock._calls_repr()}"
            )
            raise AssertionError(msg)

    def _assert_match_await_args(  # pylint: disable=too-many-branches
        self, modifier: Literal["all", "any", "last"], *args: Any, **kwargs: Any
    ) -> None:
        if not self._assert_match_args(self.__attr_mock.await_args_list, modifier, *args, **kwargs):
            if modifier == "last":
                msg = "Last await does not include arguments"
            elif modifier == "all":
                msg = "All awaits do not contain the given arguments"
            else:
                msg = "No await includes arguments"
            msg = (
                f"{msg}:\n"  # pylint:disable=protected-access
                f"{self._args_repr(*args, **kwargs)}"
                f"{self._awaits_repr()}"
            )
            raise AssertionError(msg)

    @staticmethod
    def _assert_match_args(
        args_list: umock._CallList,
        modifier: Literal["all", "any", "last"],
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        match = False
        if modifier == "last":
            args_list = umock._CallList([args_list[-1]])  # pylint:disable=protected-access
        for call_args, call_kwargs in args_list:
            arg_match = True
            kwarg_match = True
            for arg in args:
                if arg not in call_args:
                    arg_match = False
                    break
            if arg_match is False:
                if modifier != "all":
                    continue
                match = False
                break
            for kwarg in kwargs.items():
                if kwarg not in call_kwargs.items():
                    kwarg_match = False
                    break
            if kwarg_match is False and modifier == "all":
                match = False
                break
            if arg_match and kwarg_match:
                match = True
        return match

    def _awaits_repr(self) -> str:
        """Renders self.mock_awaits as a string.

        Provides similar functionality to `unittest.mock.NonCallableMock._calls_repr`.
        """
        if not self.__attr_mock.await_args_list:
            return ""
        return f"\nAwaits: {safe_repr(self.__attr_mock.await_args_list)}."

    @staticmethod
    def _args_repr(*args: Any, **kwargs: Any) -> str:
        format_args = (repr(arg) for arg in args)
        format_kwargs = (f"{name}={repr(value)}" for name, value in kwargs.items())
        return f"Arguments: call({', '.join(itertools.chain(format_args, format_kwargs))})"

    @staticmethod
    def _format_call_count(call_count: int) -> str:
        if call_count == 1:
            return "once"
        if call_count == 2:
            return "twice"
        return f"{call_count} times"

    def _validate(self) -> None:
        while len(self.__assertions) > 0:
            assertion = self.__assertions.pop()
            assertion()


class State:
    """State container for chainmock.

    Used internally by chainmock to tear down mocks.
    """

    MOCKS: Dict[Union[int, str], Mock] = {}

    @classmethod
    def get_or_create_mock(
        cls,
        target: Optional[Any],
        *,
        spec: Optional[Any] = None,
        patch_class: bool = False,
    ) -> Mock:
        """Get existing mock or create a new one if the object has not been mocked yet."""
        if target is None:  # Do not cache stubs
            Stub = type("Stub", (Mock,), {})  # Use intermediary class to attach properties
            stub = Stub(target, spec=spec, _internal=True)
            cls.MOCKS[id(stub)] = stub
            return stub  # type: ignore
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
        """Reset all mocks and return all mocked objects to their original state."""
        for mock in cls.MOCKS.values():
            mock._reset()  # pylint: disable=protected-access

    @classmethod
    def reset_state(cls) -> None:
        """Reset chainmock state."""
        cls.MOCKS = {}

    @classmethod
    def validate_mocks(cls) -> None:
        """Validate all stored mocks and their assertions."""
        mocks = cls.MOCKS
        cls.MOCKS = {}
        for mock in mocks.values():
            mock._validate()  # pylint: disable=protected-access

    @classmethod
    def teardown(cls) -> None:
        """Convenience method used in tests to reset and validate mocks."""
        cls.reset_mocks()
        cls.validate_mocks()


class Mock:
    """Mock allows mocking and spying mocked and patched objects.

    Mock should not be initialized directly. Use mocker function instead.
    """

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
        self.__target = target
        self.__spec = spec
        self.__patch = patch
        self.__mock = (
            patch.start() if patch else umock.MagicMock(spec=spec if spec is not None else target)
        )
        self.__assertions: Dict[str, Assert] = {}
        self.__object_patches: List[
            umock._patch[Any]  # pylint: disable=unsubscriptable-object
        ] = []
        self.__patch_class: bool = patch_class

    def __call__(self, *args: Any, **kwargs: Any) -> Mock:
        """Return self when Mock is called directly.

        This allows mocking methods that are properties but are also callable.
        """
        return self

    def spy(self, name: str) -> Assert:
        """Spy an attribute.

        This wraps the given attribute so that functions or methods still return
        their original values and work as if they were not mocked. With spies,
        you can assert that a function or method was called without mocking it.

        Examples:
            Assert that the method `add_tea` was called once:

            >>> teapot = Teapot()
            >>> teapot.add_tea("white tea")
            'loose white tea'
            >>> mocker(teapot).spy("add_tea").called_once()
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("white tea")
            'loose white tea'

            Assert that the method `add_tea` was called with specific arguments:

            >>> teapot = Teapot()
            >>> teapot.add_tea("white tea", loose=False)
            'bagged white tea'
            >>> mocker(teapot).spy("add_tea").called_last_with("green tea", loose=True)
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("green tea", loose=True)
            'loose green tea'

        Args:
            name: Attribute name to spy.

        Returns:
            Assert instance.

        Raises:
            ValueError: Raised if the given attribute name is empty.
            RuntimeError: If trying to spy stubs or patched objects. Also raised
                if trying to spy a mocked attribute.
        """
        if self.__target is None:
            raise RuntimeError("Spying is not available for stubs. Call 'mock' instead.")
        if self.__patch is not None:
            raise RuntimeError("Spying is not available for patched objects. Call 'mock' instead.")
        if not name:
            raise ValueError("Attribute name cannot be empty.")
        if cached := self.__assertions.get(name):
            if cached._kind == "mock":  # pylint: disable=protected-access
                raise RuntimeError(
                    f"Attribute '{name}' has already been mocked. Can't spy a mocked attribute."
                )
            return cached
        parsed_name = self.__remove_name_mangling(name)
        original = getattr(self.__target, parsed_name)
        attr_mock = self.__get_patch_attr_mock(
            self.__mock, parsed_name, create=True, force_property=False, force_async=False
        )
        parameters = tuple(inspect.signature(original).parameters.keys())
        is_class_method = self.__get_method_type(parsed_name, classmethod)
        is_static_method = self.__get_method_type(parsed_name, staticmethod)

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
            patch = umock.patch.object(
                self.__target, parsed_name, new_callable=lambda: async_pass_through
            )
        else:
            patch = umock.patch.object(
                self.__target, parsed_name, new_callable=lambda: pass_through
            )
        patch.start()
        self.__object_patches.append(patch)
        assertion = Assert(self, attr_mock, parsed_name, kind="spy", _internal=True)
        self.__assertions[name] = assertion
        return assertion

    def __get_method_type(
        self,
        name: str,
        method_type: Union[Type[classmethod], Type[staticmethod]],  # type: ignore # mypy bug?
    ) -> bool:
        try:
            return isinstance(inspect.getattr_static(self.__target, name), method_type)
        except AttributeError:
            # Inspecting proxied objects raises AttributeError
            if hasattr(self.__target, "__mro__"):
                for cls in inspect.getmro(self.__target):  # type: ignore
                    method = vars(cls).get(name)
                    if method is not None:
                        return isinstance(method, method_type)
            return False

    def mock(
        self,
        name: str,
        *,
        create: bool = False,
        force_property: bool = False,
        force_async: bool = False,
    ) -> Assert:
        """Mock an attribute.

        The given attribute is mocked and the mock catches all the calls to it.
        If not return value is set, `None` is returned by default.

        Examples:
            Assert that the method `add_tea` was called once:

            >>> teapot = Teapot()
            >>> teapot.add_tea("white tea")
            'loose white tea'
            >>> mocker(teapot).mock("add_tea").called_once()
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("white tea")

            Replace the return value of the `add_tea` method:

            >>> teapot = Teapot()
            >>> teapot.add_tea("green tea")
            'loose green tea'
            >>> mocker(teapot).mock("add_tea").return_value("mocked")
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("green tea")
            'mocked'

            Assert that the method `add_tea` was called with a specific argument
            while also replacing the return value:

            >>> teapot = Teapot()
            >>> teapot.add_tea("white tea", loose=False)
            'bagged white tea'
            >>> mocker(teapot).mock("add_tea").match_args_last_call(
            ...     "green tea"
            ... ).return_value("mocked")
            <chainmock._api.Assert object at ...>
            >>> teapot.add_tea("green tea", loose=True)
            'mocked'

        Args:
            name: Attribute name to mock.
            create: Force creation of the attribute if it does not exist. By
                mocking non-existing attributes raises an AttributeError. If you
                want force the creation and ignore the error, set this to True.
                This can be useful for testing dynamic attributes set during
                runtime.
            force_property: Force the mock to be a `PropertyMock`. This can be
                used to create properties on stubs or force the mock to be a
                `PropertyMock` if the automatic detection from spec does not
                work.
            force_async: Force the mock to be a `AsyncMock`. This can be
                used to create async methods on stubs or force the mock to be a
                `AsyncMock` if the automatic detection from spec does not work.

        Returns:
            Assert instance.

        Raises:
            ValueError: Raised if the given attribute name is empty.
            RuntimeError: If trying to mock a spied attribute.
        """
        if cached := self.__assertions.get(name):
            if cached._kind == "spy":  # pylint: disable=protected-access
                raise RuntimeError(
                    f"Attribute '{name}' has already been spied. Can't mock a spied attribute."
                )
            return cached
        parts = name.split(".")
        parsed_name = self.__remove_name_mangling(parts[0])
        parts = parts[1:]
        if not parsed_name:
            raise ValueError("Attribute name cannot be empty.")
        if self.__target is None:
            assertion = self.__stub_attribute(
                parsed_name,
                parts,
                create=create,
                force_property=force_property,
                force_async=force_async,
            )
        elif self.__patch is not None:
            assertion = self.__patch_attribute(
                parsed_name,
                parts,
                create=create,
                force_property=force_property,
                force_async=force_async,
            )
        else:
            original = self.__get_original(parsed_name, create)
            assertion = self.__mock_attribute(
                parsed_name,
                parts,
                original,
                create=create,
                force_property=force_property,
                force_async=force_async,
            )
        assertion.return_value(None)
        self.__assertions[name] = assertion
        return assertion

    def __remove_name_mangling(self, name: str) -> str:
        """Get method the real method name if uses name mangling."""
        if inspect.ismodule(self.__target) or name.endswith("__") or not name.startswith("__"):
            return name
        if inspect.isclass(self.__target):
            class_name = self.__target.__name__
        else:
            # Get class name from an instance
            class_name = self.__target.__class__.__name__
        return f"_{class_name.lstrip('_')}__{name.lstrip('_')}"

    def __get_original(self, name: str, create: bool) -> Optional[Any]:
        try:
            return getattr(self.__target, name)
        except AttributeError:
            if create is True:
                return None
            raise

    def __stub_attribute(
        self, name: str, parts: List[str], *, create: bool, force_property: bool, force_async: bool
    ) -> Assert:
        if name in list(set(dir(Mock)) - set(dir(type))):
            raise ValueError(f"Cannot replace Mock internal attribute {name}")
        attr_mock = self.__get_stub_attr_mock(
            name, create=create, force_property=force_property, force_async=force_async
        )
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 0:
            # Support for chaining methods
            assertion.return_value(self)
            assertion = self.mock(".".join(parts))
        return assertion

    def __get_stub_attr_mock(
        self, name: str, *, create: bool, force_property: bool, force_async: bool
    ) -> AnyMock:
        if self.__spec is not None:
            try:
                original = getattr(self.__spec, name)
            except AttributeError:
                if create is True:
                    if force_property:
                        return self.__get_stub_property_mock(name)
                    attr_mock = umock.AsyncMock() if force_async else umock.MagicMock()
                    setattr(self, name, attr_mock)
                    return attr_mock
                raise
            if isinstance(original, property):
                return self.__get_stub_property_mock(name)
        if force_property:
            return self.__get_stub_property_mock(name)
        if force_async:
            attr_mock = umock.AsyncMock()
        else:
            attr_mock = getattr(self.__mock, name)
        setattr(self, name, attr_mock)
        return attr_mock

    def __get_stub_property_mock(self, name: str) -> AnyMock:
        attr_mock = umock.PropertyMock()
        setattr(type(self), name, attr_mock)
        return attr_mock

    def __patch_attribute(
        self, name: str, parts: List[str], *, create: bool, force_property: bool, force_async: bool
    ) -> Assert:
        if not self.__patch_class and self.__patch and inspect.isclass(self.__patch.temp_original):
            attr_mock: AnyMock = self.__get_patch_attr_mock(
                self.__mock(),
                name,
                create=create,
                force_property=force_property,
                force_async=force_async,
            )
        else:
            attr_mock = self.__get_patch_attr_mock(
                self.__mock, name, create=create, force_property=False, force_async=force_async
            )
        assertion = Assert(self, attr_mock, name, _internal=True)
        if len(parts) > 0:
            # Support for chaining methods
            stub = Mock(_internal=True)
            assertion.return_value(stub)
            assertion = stub.mock(".".join(parts))
        return assertion

    def __get_patch_attr_mock(
        self, mock: AnyMock, name: str, *, create: bool, force_property: bool, force_async: bool
    ) -> AnyMock:
        try:
            attr_mock = getattr(mock, name)
        except AttributeError:
            if create is True:
                if force_property:
                    return self.__get_patch_property_mock(mock, name)
                attr_mock = umock.AsyncMock() if force_async else umock.MagicMock()
                setattr(mock, name, attr_mock)
                return attr_mock
            raise
        if force_property or (
            not self.__patch_class
            and self.__patch
            and isinstance(getattr(self.__patch.temp_original, name), property)
        ):
            return self.__get_patch_property_mock(mock, name)
        if force_async:
            attr_mock = umock.AsyncMock()
            setattr(mock, name, attr_mock)
        return attr_mock

    @staticmethod
    def __get_patch_property_mock(mock: AnyMock, name: str) -> AnyMock:
        attr_mock = umock.PropertyMock()
        setattr(type(mock), name, attr_mock)
        return attr_mock

    def __mock_attribute(
        self,
        name: str,
        parts: List[str],
        original: Optional[Any],
        *,
        create: bool,
        force_property: bool,
        force_async: bool,
    ) -> Assert:
        patch: umock._patch[Any]  # pylint: disable=unsubscriptable-object
        if inspect.ismodule(self.__target) and not callable(original):
            # Support mocking module attributes/variables
            patch = umock.patch.object(self.__target, name, new=None, create=create)
            patch.start()
            self.__object_patches.append(patch)
            attr_mock = umock.NonCallableMagicMock()
        else:
            new_callable = None
            if force_property or (original is not None and isinstance(original, property)):
                new_callable = umock.PropertyMock
            elif force_async:
                new_callable = umock.AsyncMock
            patch = umock.patch.object(
                self.__target, name, new_callable=new_callable, create=create
            )
            attr_mock = patch.start()
            self.__object_patches.append(patch)
        assertion = Assert(self, attr_mock, name, patch=patch, _internal=True)
        if len(parts) > 0:
            # Support for chaining methods
            stub = Mock(_internal=True)
            assertion.return_value(stub)
            assertion = stub.mock(".".join(parts))
        return assertion

    def _reset(self) -> None:
        while len(self.__object_patches) > 0:
            patch = self.__object_patches.pop()
            patch.stop()
        if self.__patch is not None:
            self.__patch.stop()

    def _validate(self) -> None:
        for key in list(self.__assertions):
            assertion = self.__assertions.pop(key)
            assertion._validate()  # pylint: disable=protected-access


def mocker(
    target: Optional[Union[str, Any]] = None,
    *,
    spec: Optional[Any] = None,
    patch_class: bool = False,
    **kwargs: Any,
) -> Mock:
    """Main entrypoint for chainmock.

    Depending on the arguments you pass to `mocker` function, it provides
    different functionality. Supported functionalities are partial mocking (and
    spying), stubbing, and patching. See detailed explanations below.

    # Partial mocking
    If mocker is invoked with an object (eg. class, instance, module), the named
    members (attributes) on the object (target) can be mocked or spied
    individually. For example, by calling `mocker(SomeClass)` you are setting
    the target to a class. The original object is not modified until you
    explicitly spy or mock it's members.

    # Stubbing
    If mocker is invoked without a target, a stub is created. For example, by
    calling `mocker()`. The created stub doesn't have any methods or attributes
    until you explicitly set them.

    # Patching
    If the given target is a string, the target is imported and the specified
    object is replaced with a mock. The string should be in form
    'package.module.ClassName' and the target must be importable from the
    environment you are calling `mocker`. As an example,
    mocker('some_module.SomeClass') would replace the `SomeClass` class in the
    module `some_module`. After patching the object, you can set assertions and
    return values on the mock that replaced the object.

    Patching is useful especially when you want to replace all the new instances
    of a class with a mock. Therefore if you patch a class, chainmock patches
    the class instances by default. If you wish to patch the class instead, set
    `patch_class` argument to True. If you do not need to patch new instances of
    a class, most use cases can be covered with partial mocking.

    For more details about patching see:
    [unittest.mock.html#patch](
    https://docs.python.org/3/library/unittest.mock.html#patch)

    Examples:
        _Partially mock_ the `Teapot` class:

        >>> # First let's fill a teapot and boil the water without mocking
        >>> teapot = Teapot()
        >>> teapot.state
        'empty'
        >>> teapot.fill()
        >>> teapot.state
        'full'
        >>> teapot.boil()
        >>> teapot.state
        'boiling'

        >>> # Now let's try the same thing but also mock the boil call
        >>> mocker(Teapot).mock("boil")
        <chainmock._api.Assert object at ...>
        >>> teapot = Teapot()
        >>> teapot.state
        'empty'
        >>> teapot.fill()  # fill still works because only boil method is mocked
        >>> teapot.state
        'full'
        >>> teapot.boil()  # state is not updated because boil method is mocked
        >>> teapot.state
        'full'

        _Create a stub_ and attach methods to it:

        >>> stub = mocker()
        >>> stub.mock("my_method").return_value("It works!")
        <chainmock._api.Assert object at ...>
        >>> stub.mock("another_method").side_effect(RuntimeError("Oh no!"))
        <chainmock._api.Assert object at ...>
        >>> stub.my_method()
        'It works!'
        >>> stub.another_method()
        Traceback (most recent call last):
          ...
        RuntimeError: Oh no!

        Replace all the instances of `SomeClass` with a mock by _patching_ it:

        >>> class SomeClass:
        ...    def method(self, arg):
        ...        pass
        ...
        >>> mocked = mocker("__main__.SomeClass")
        >>> # SomeClass instances are now replaced by a mock
        >>> some_class = SomeClass()
        >>> some_class.method("foo")
        >>> # We can change return values, assert call counts or arguments
        >>> mocked.mock("method").return_value("mocked")
        <chainmock._api.Assert object at ...>

    Args:
        target: The target to mock or spy. By leaving out the target, a stub is
            created. If the target is a string, the object in the given path is
            mocked and if the target is any other object like class or module,
            you can mock and spy individual functions and methods using the
            returned mock instance.
        spec: Spec acts as the specification for the created mock objects. It
            can be either a list of strings or an existing object (a class or
            instance). Accessing any attribute not in the given spec raises an
            AttributeError. Spec can be useful if you want to create stubs with
            a certain spec. Otherwise it is usually not needed because spec is
            automatically set from the given target object.
        patch_class: By default, patching an object (setting target to a string)
            allows mocking attributes of the instance of a given target class.
            If you want to mock the class itself, instead of it's instance, set
            this to True. Note that it is usually easier to just use partial
            mocking if you need to patch the class.
        **kwargs: You can give arbitrary keyword arguments to quickly set mocked
            attributes and properties on the created Mock instance.

    Returns:
        Mock instance.
    """
    mock = State.get_or_create_mock(target, spec=spec, patch_class=patch_class)
    for name, value in kwargs.items():
        # Create kwargs as properties for stubs without a spec
        force_property = target is None and spec is None
        mock.mock(name, force_property=force_property).return_value(value)
    return mock
