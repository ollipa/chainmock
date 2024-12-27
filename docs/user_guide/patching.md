# Patching

Patching allows you to replace a specified object with a mock, particularly useful when you need to replace all new instances of a class with a mock. If the target given to `mocker` function is a string in the form of `package.module.ClassName`, Chainmock imports the target and replaces the specified object with a mock. After patching the object, you can set assertions and return values on the mock, controlling its behavior for your tests.

By default, Chainmock patches class instances. However, if you prefer to patch the class itself, you can set the `patch_class` argument to `True`.

## Mocking new instances

Replace all the instances of `SomeClass` with a mock by patching it:

```python
#! remove-prefix
>>> class SomeClass:
...     def method(self, arg):
...         pass
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

Note that patching uses Python's import system, so the class must be importable from the environment where you're running the tests.

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
