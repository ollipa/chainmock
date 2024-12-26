# Async mocking

Chainmock provides comprehensive support for mocking and asserting async methods. You can mock async methods, set their return values, and verify how they were awaited.

## Basic async mocking

To mock an async method, use the regular mock() function. Chainmock will automatically detect that the method is async and create an appropriate async mock:

```python
>>> async def mock_async_method():
...     mocker(Teapot).mock("timer").return_value("mocked")
...     assert await Teapot().timer(1, 2) == "mocked"
>>> asyncio.run(mock_async_method()) #! hidden
>>> State.teardown() #! hidden

```

You can force a mock to be async by setting `force_async=True`, which is useful when working with stubs or when automatic detection doesn't work:

```python
>>> async def mock_forced_async():
...     stub = mocker()
...     stub.mock("async_method", force_async=True).return_value("forced async")
...     assert await stub.async_method() == "forced async"
>>> asyncio.run(mock_forced_async()) #! hidden
>>> State.teardown() #! hidden

```

## Asserting await calls

### Basic assertions

Assert that an async method was awaited at least once:

```python
>>> async def assert_awaited():
...     mocker(Teapot).mock("timer").awaited()
...     await Teapot().timer(5)
>>> asyncio.run(assert_awaited()) #! hidden
>>> State.teardown() #! hidden

```

Assert that an async method was never awaited:

```python
>>> mocker(Teapot).mock("timer").not_awaited()
<chainmock._api.Assert object at ...>
>>> State.teardown() #! hidden

```

### Advanced assertions

You can also assert the number of times an async method was awaited:

```python
>>> async def assert_awaited():
...     mocker(Teapot).mock("open").awaited_once()
...     mocker(Teapot).mock("close").awaited_twice()
...     await Teapot().open()
...     await Teapot().close()
...     await Teapot().close()
>>> asyncio.run(assert_awaited()) #! hidden
>>> State.teardown() #! hidden

```

Also more advanced call count assertions are supported:

```python
>>> async def assert_await_counts():
...     mock = mocker(Teapot)
...     # Exact count
...     mock.mock("timer").await_count(3)
...     await Teapot().timer(1)
...     await Teapot().timer(2)
...     await Teapot().timer(3)
...
...     # At least once
...     mock.mock("open").await_count_at_least(1)
...     await Teapot().open()
...
...     # At most twice
...     mock.mock("close").await_count_at_most(2)
...     await Teapot().close()
...     await Teapot().close()
>>> asyncio.run(assert_await_counts()) #! hidden
>>> State.teardown() #! hidden

```

## Asserting await arguments

Assert that the last await was with specific arguments:

```python
>>> async def assert_last_await():
...     mocker(Teapot).mock("timer").awaited_last_with(5, seconds=30)
...     await Teapot().timer(5, seconds=30)
>>> asyncio.run(assert_last_await()) #! hidden
>>> State.teardown() #! hidden

```

Assert that any await included specific arguments:

```python
>>> async def assert_any_await():
...     mocker(Teapot).mock("timer").any_await_with(5, seconds=30)
...     await Teapot().timer(2)
...     await Teapot().timer(5, seconds=30)
>>> asyncio.run(assert_any_await()) #! hidden
>>> State.teardown() #! hidden

```

Match partial arguments in awaits:

```python
>>> async def assert_partial_args():
...     # Match just the minutes parameter
...     mock = mocker(Teapot).mock("timer")
...     mock.match_args_any_await(5)
...     await Teapot().timer(5, seconds=30)
...
...     # Match just the seconds parameter
...     mock.match_args_any_await(seconds=45)
...     await Teapot().timer(3, seconds=45)
>>> asyncio.run(assert_partial_args()) #! hidden
>>> State.teardown() #! hidden

```

Assert a sequence of awaits:

```python
>>> from chainmock.mock import call
>>> async def assert_await_sequence():
...     mock = mocker(Teapot).mock("timer")
...     mock.has_awaits([
...         call(5),
...         call(3, seconds=30)
...     ])
...     await Teapot().timer(5)
...     await Teapot().timer(3, seconds=30)
>>> asyncio.run(assert_await_sequence()) #! hidden
>>> State.teardown() #! hidden

```

## Side effects and return values

You can use `return_value()` and `side_effect()` with async mocks just like with regular mocks:

```python
>>> async def mock_async_returns():
...     # Return a fixed value
...     mock = mocker(Teapot)
...     mock.mock("timer").return_value(42)
...     assert await Teapot().timer(5) == 42
...
...     # Return a sequence of values
...     mock.mock("open").side_effect([
...         "opened",
...         "already open",
...         Exception("stuck!")
...     ])
...     assert await Teapot().open() == "opened"
...     assert await Teapot().open() == "already open"
...     try:
...         await Teapot().open()
...     except Exception as e:
...         assert str(e) == "stuck!"
>>> asyncio.run(mock_async_returns()) #! hidden
>>> State.teardown() #! hidden

```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
