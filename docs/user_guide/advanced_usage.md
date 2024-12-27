# Advanced usage

## Non-existent attributes

You can also mock attributes that don't exist. By default, Chainmock will raise an `AttributeError` if you try to mock a non-existent attribute:

```python
#! remove-prefix
>>> mocker(Teapot).mock("new_method")
Traceback (most recent call last):
  ...
AttributeError: type object 'Teapot' has no attribute 'new_method'
>>> State.teardown() #! hidden

```

Allow creation of the new method explicitly with the `create=True` parameter:

```python
#! remove-prefix
>>> mocker(Teapot).mock("new_method", create=True).return_value("mocked")
<chainmock._api.Assert object at ...>
>>> assert Teapot().new_method() == "mocked"
>>> State.teardown() #! hidden

```

## Mocking builtins

Chainmock allows you to mock built-in functions and classes, such as `open`. You can mock built-in functions and classes directly, just like any other attribute:

```python
#! remove-prefix
>>> import builtins
>>> mock_file = mocker()
>>> mock_file.mock("read").return_value("mocked1").called_once()
<chainmock._api.Assert object at ...>
>>> mocker(builtins).mock("open").return_value(mock_file)
<chainmock._api.Assert object at ...>
>>> assert open("foo", encoding="utf8").read() == "mocked1"
>>> State.teardown() #! hidden

```

## Chained method calls

You can mock chained method access by using dot notation:

```python
#! remove-prefix
>>> from pathlib import Path
>>> # Mock a chain of path operations
>>> mocker(Path).mock("home.joinpath.resolve").return_value("/mocked/home/path")
<chainmock._api.Assert object at ...>
>>> assert Path.home().joinpath("test").resolve() == "/mocked/home/path"
>>> State.teardown() #! hidden

```

## Mocking new instances

When you need to mock every new instance of a class that gets created during testing, Chainmock provides a straightforward way to do this using patching.

```python
#! remove-prefix
>>> class SomeClass:
...     def method(self):
...         return "original"
...
>>> mocked = mocker("__main__.SomeClass")
>>> # Any new instance will use the mocked method
>>> mocked.mock("method").return_value("mocked")
<chainmock._api.Assert object at ...>
>>> State.teardown() #! hidden

```

Note that instance mocking uses Python's import system, so the class must be importable from the environment where you're running the tests.

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
