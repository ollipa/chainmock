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
>>> mocker(Teapot).mock("boil").called_once()
<chainmock._api.Assert object at ...>
>>> Teapot().boil()
>>> State.teardown() #! hidden

```

Assert that the method `boil` was called at least once but not more than twice:

```python
>>> mocker(teapot).mock("boil").call_count_at_least(1).call_count_at_most(2)
<chainmock._api.Assert object at ...>
>>> teapot.boil()
>>> teapot.boil()
>>> State.teardown() #! hidden

```

Assert that the method `pour` was called exactly three times:

```python
>>> mocker(teapot).mock("pour").call_count(3)
<chainmock._api.Assert object at ...>
>>> teapot.pour()
>>> teapot.pour()
>>> teapot.pour()
>>> State.teardown() #! hidden

```

### Assert call arguments

Assert that the method `add_tea` was called once with the argument `puehr`:

```python
>>> mocker(Teapot).mock("add_tea").called_once_with("puehr")
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("puehr")
>>> State.teardown() #! hidden

```

Assert that the method `add_tea` was called once with the argument `oolong` and once with the argument `black`:

```python
>>> from chainmock.mock import call
>>> mocker(Teapot).mock("add_tea").has_calls([call("oolong"), call("black")])
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("oolong")
>>> Teapot().add_tea("black")
>>> State.teardown() #! hidden

```

Assert that the method `add_tea` was called at least once with the keyword argument `loose=True`:

```python
>>> mocker(Teapot).mock("add_tea").match_args_any_call(loose=True)
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("oolong", loose=True)
>>> State.teardown() #! hidden

```

### Mock return values and side effects

Mock the return value of method `brew`:

```python
>>> mocker(Teapot).mock("brew").return_value("mocked")
<chainmock._api.Assert object at ...>
>>> Teapot().brew()
'mocked'
>>> State.teardown() #! hidden

```

Raise an exception when the method `brew` is called:

```python
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
>>> State.teardown() #! hidden

```

### Chaining assertions

Chainmock allows you to chain multiple assertions together, making it easy to test complex interactions in your code. For example, you can assert that a method was called with specific arguments and return a specific value:

```python
>>> (mocker(Teapot)
...    .mock("add_tea")
...    .called_once_with("green")
...    .return_value("loose green tea"))
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("green")
'loose green tea'
>>> State.teardown() #! hidden

```

Another example, assert that the method `add_tea` was called at least once but not more than twice with the arguments `green` and `black`, and return a specific value:

```python
>>> (mocker(Teapot)
...    .mock("add_tea")
...    .call_count_at_least(1)
...    .call_count_at_most(2)
...    .has_calls([call("green"), call("black")])
...    .return_value("mocked tea"))
<chainmock._api.Assert object at ...>
>>> Teapot().add_tea("green")
'mocked tea'
>>> Teapot().add_tea("black")
'mocked tea'

```

## Features

### Partial mocking

Partial mocking and spying of objects, allows you to mock or spy only specific methods or attributes of an object. This is useful when you want to mock or spy only a single method of an object, while leaving the rest of the object's behavior intact.

If `mocker` is invoked with an object (eg. class, instance, module), the named members of the object can be mocked or spied individually. For example, by calling `mocker(SomeClass)` you are setting the mocking target to a class. The original object is not modified until you explicitly spy or mock it's members.

_Partially mock_ the `Teapot` class:

```python
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

```

```python
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
>>> State.teardown() #! hidden

```

### Spying

Spying allows monitoring specific interactions with objects or methods in your code. When you create a spy, you essentially "watch" the behavior of the target object or method, without changing its original functionality. With spies, you can assert that a function or method was called without mocking it.

Assert that the method `add_tea` was called once:

```python
>>> teapot = Teapot()
>>> teapot.add_tea("white tea")
'loose white tea'
>>> mocker(teapot).spy("add_tea").called_once()
<chainmock._api.Assert object at ...>
>>> teapot.add_tea("white tea")
'loose white tea'
>>> State.teardown() #! hidden

```

Assert that the method add_tea was called with specific arguments:

```python
>>> teapot = Teapot()
>>> teapot.add_tea("white tea", loose=False)
'bagged white tea'
>>> mocker(teapot).spy("add_tea").called_last_with("green tea", loose=True)
<chainmock._api.Assert object at ...>
>>> teapot.add_tea("green tea", loose=True)
'loose green tea'
>>> State.teardown() #! hidden

```

### Stubbing

If `mocker` is invoked without a target, it creates a stub, an empty object that doesn't have any methods or attributes. For example, by calling `mocker()`. You can then explicitly set these methods and attributes as needed during testing. This is useful for simulating behavior within your test environment, ensuring that your code interacts as expected with the stubbed object.

If `mocker` is invoked without a target, a stub is created. For example, by calling `mocker()`. The created stub doesn't have any methods or attributes until you explicitly set them.

Create a _stub_ and attach methods to it:

```python
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
>>> State.teardown() #! hidden

```

### Patching

Patching allows you to replace a specified object with a mock, particularly useful when you need to replace all new instances of a class with a mock. If the target given to `mocker` function is a string in the form of `package.module.ClassName`, Chainmock imports the target and replaces the specified object with a mock. After patching the object, you can set assertions and return values on the mock, controlling its behavior for your tests.

By default, Chainmock patches class instances. However, if you prefer to patch the class itself, you can set the `patch_class` argument to `True`.

Replace all the instances of `SomeClass` with a mock by patching it:

```python
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
>>> State.teardown() #! hidden

```

## Utility objects

`chainmock.mock` module contains some re-exports from standard library `unittest.mock` module for convenience. It also contains utility objects that are helpful when asserting values in tests. Often you don't necessarily care about the exact value of something, but you might want to make sure that it is of a certain type.

`unittest.mock` module contains `ANY` object that can be compared to any other object and the comparison returns `True`. `chainmock.mock` contains the following additional objects: `ANY_BOOL`, `ANY_BYTES`, `ANY_COMPLEX`, `ANY_DICT`, `ANY_FLOAT`, `ANY_INT`, `ANY_LIST`, `ANY_SET`, `ANY_STR`, and `ANY_TUPLE`.

```python
from chainmock import mock

assert {
    "bool": mock.ANY_BOOL,
    "bytes": mock.ANY_BYTES,
    "complex": mock.ANY_COMPLEX,
    "dict": mock.ANY_DICT,
    "float": mock.ANY_FLOAT,
    "int": mock.ANY_INT,
    "list": mock.ANY_LIST,
    "set": mock.ANY_SET,
    "string": mock.ANY_STR,
    "tuple": mock.ANY_TUPLE,
} == {
    "bool": True,
    "bytes": b"some_bytes",
    "complex": complex("1+2j"),
    "dict": {"nested": "value"},
    "float": 1.23,
    "int": 7983,
    "list": [1, 2, 3],
    "set": {"foo", "bar"},
    "string": "some_string",
    "tuple": (1, 2),
}
```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
