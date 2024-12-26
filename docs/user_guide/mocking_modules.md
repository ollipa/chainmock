# Mocking modules

Chainmock allows you to mock entire modules as well as specific module attributes or variables. This is particularly useful when you need to modify the behavior of imported modules during testing.

## Mocking module variables

You can mock module variables and attributes directly. This is useful when you need to override configuration values, constants, or other module-level variables during testing.

```python
#! remove-prefix
>>> import socket
>>> mocker(socket).mock("AF_INET").return_value(42)
<chainmock._api.Assert object at ...>
>>> assert socket.AF_INET == 42
>>> State.teardown() #! hidden

```

## Mocking environment variables

A common use case is mocking environment variables in the `os` module:

```python
#! remove-prefix
>>> import os
>>> # Mock os.environ to return a custom value
>>> mocker(os).mock("environ").return_value({"MY_ENV": "test_value"})
<chainmock._api.Assert object at ...>
>>> assert os.environ["MY_ENV"] == "test_value"
>>> State.teardown() #! hidden

```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
