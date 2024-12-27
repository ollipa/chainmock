# Getting started

Chainmock is a Python library designed to simplify and streamline the process of mocking, stubbing, and patching objects in your test code. It is built on top of the Python standard library `unittest.mock` module, providing a more intuitive and convenient interface for performing these tasks.

Because Chainmock uses Python standard library mocks under the hood, it is fully compatible with all the same features and functionality. In other words, everything that is possible with `unittest.mock` is also possible with Chainmock.

To get started with using Chainmock, import the `mocker` function:

```python
from chainmock import mocker
```

`mocker` function is the main entrypoint to Chainmock. It provides different functionality depending on the arguments you pass to it. Supported functionalities are partial mocking (and spying), stubbing, and patching.

## What you can do with Chainmock?

!!! note

    These examples contain just a small part of Chainmock's functionality. For more details and examples, see the [API reference](../api_reference.md).

### Assert call counts

Assert that the method `boil` was called exactly once:

```python
#! remove-prefix
>>> mocker(Teapot).mock("boil").called_once()
<chainmock._api.Assert object at ...>
>>> Teapot().boil() #! hidden
>>> State.teardown() #! hidden

```

Assert that the method `boil` was called at least once but not more than twice:

```python
#! remove-prefix
>>> mocker(teapot).mock("boil").call_count_at_least(1).call_count_at_most(2)
<chainmock._api.Assert object at ...>
>>> teapot.boil() #! hidden
>>> teapot.boil() #! hidden
>>> State.teardown() #! hidden

```

Assert that the method `pour` was called exactly three times:

```python
#! remove-prefix
>>> mocker(teapot).mock("pour").call_count(3)
<chainmock._api.Assert object at ...>
>>> teapot.pour() #! hidden
>>> teapot.pour() #! hidden
>>> teapot.pour() #! hidden
>>> State.teardown() #! hidden

```

### Assert call arguments

Assert that the method `add_tea` was called once with the argument `puehr`:

```python
#! remove-prefix
>>> mocker(Teapot).mock("add_tea").called_once_with("puehr")
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("puehr") #! hidden
>>> State.teardown() #! hidden

```

Assert that the method `add_tea` was called once with the argument `oolong` and once with the argument `black`:

```python
#! remove-prefix
>>> from chainmock.mock import call
>>> mocker(Teapot).mock("add_tea").has_calls([call("oolong"), call("black")])
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("oolong")
>>> Teapot().add_tea("black")
>>> State.teardown() #! hidden

```

Assert that the method `add_tea` was called at least once with the keyword argument `loose=True`:

```python
#! remove-prefix
>>> mocker(Teapot).mock("add_tea").match_args_any_call(loose=True)
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("oolong", loose=True)
>>> State.teardown() #! hidden

```

### Mock return values and side effects

Mock the return value of method `brew`:

```python
#! remove-prefix
>>> mocker(Teapot).mock("brew").return_value("mocked")
<chainmock._api.Assert object at ...>
>>> assert Teapot().brew() == "mocked"
>>> State.teardown() #! hidden

```

Raise an exception when the method `brew` is called:

```python
#! remove-prefix
>>> mocker(Teapot).mock("brew").side_effect(Exception("No tea!"))
<chainmock._api.Assert object at ...>
>>> Teapot().brew()
Traceback (most recent call last):
  ...
Exception: No tea!
>>> State.teardown() #! hidden

```

Use a list to return a sequence of values:

```python
#! remove-prefix
>>> mocker(teapot).mock("pour").side_effect([2, 1, Exception("empty")])
<chainmock._api.Assert object at ...>
>>> assert teapot.pour() == 2
>>> assert teapot.pour() == 1
>>> teapot.pour()
Traceback (most recent call last):
  ...
Exception: empty
>>> State.teardown() #! hidden

```

### Chaining assertions

Chainmock allows you to chain multiple assertions together, making it easy to test complex interactions in your code. For example, you can assert that a method was called with specific arguments and return a specific value:

```python
#! remove-prefix
>>> mocker(Teapot).mock("add_tea").called_once_with("green").return_value("mocked")
<chainmock._api.Assert object at ...>
>>> assert Teapot().add_tea("green") == "mocked"
>>> State.teardown() #! hidden

```

Another example, assert that the method `add_tea` was called at least once but not more than twice with the arguments `green` and `black`, and return a specific value:

```python
#! remove-prefix
>>> mocked = mocker(Teapot).mock("add_tea")
>>> mocked.call_count_at_least(1)
<chainmock._api.Assert object at ...>
>>> mocked.call_count_at_most(2)
<chainmock._api.Assert object at ...>
>>> mocked.has_calls([call("green"), call("black")])
<chainmock._api.Assert object at ...>
>>> mocked.return_value("mocked tea")
<chainmock._api.Assert object at ...>
>>> assert Teapot().add_tea("green") == "mocked tea"
>>> assert Teapot().add_tea("black") == "mocked tea"

```

## Utility objects

`chainmock.mock` module contains some re-exports from standard library `unittest.mock` module for convenience. It also contains utility objects that are helpful when asserting values in tests. Often you don't necessarily care about the exact value of something, but you might want to make sure that it is of a certain type.

`unittest.mock` module contains `ANY` object that can be compared to any other object and the comparison returns `True`. `chainmock.mock` contains the following additional objects: `ANY_BOOL`, `ANY_BYTES`, `ANY_COMPLEX`, `ANY_DICT`, `ANY_FLOAT`, `ANY_INT`, `ANY_LIST`, `ANY_SET`, `ANY_STR`, and `ANY_TUPLE`.

```python
#! remove-prefix
>>> from chainmock import mock
>>>
>>> assert {
...     "bool": mock.ANY_BOOL,
...     "bytes": mock.ANY_BYTES,
...     "complex": mock.ANY_COMPLEX,
...     "dict": mock.ANY_DICT,
...     "float": mock.ANY_FLOAT,
...     "int": mock.ANY_INT,
...     "list": mock.ANY_LIST,
...     "set": mock.ANY_SET,
...     "string": mock.ANY_STR,
...     "tuple": mock.ANY_TUPLE,
... } == {
...     "bool": True,
...     "bytes": b"some_bytes",
...     "complex": complex("1+2j"),
...     "dict": {"nested": "value"},
...     "float": 1.23,
...     "int": 7983,
...     "list": [1, 2, 3],
...     "set": {"foo", "bar"},
...     "string": "some_string",
...     "tuple": (1, 2),
... }
>>> State.teardown() #! hidden

```

These objects are useful in argument matching when asserting calls to mocked methods. For example:

```python
#! remove-prefix
>>> mocker(Teapot).mock("add_tea").called_once_with(mock.ANY_STR, mock.ANY_BOOL)
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("green", True)
>>> State.teardown() #! hidden

```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
