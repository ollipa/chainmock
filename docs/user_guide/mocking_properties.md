# Mocking properties

Chainmock provides robust support for mocking properties in Python classes. You can mock properties using the standard `mock()` method - Chainmock will automatically detect that the attribute is a property and create an appropriate property mock.

## Basic property mocking

Mock a property to return a specific value:

```python

>>> mocker(Teapot).mock("state").return_value("mocked state")
<chainmock._api.Assert object at ...>
>>> teapot = Teapot()
>>> teapot.state
'mocked state'
>>> State.teardown() #! hidden

```

Sometimes you might want to force an attribute to be mocked as a property, especially when working with stubs or when automatic detection doesn't work. Use the `force_property=True` parameter:

```python
>>> stub = mocker()
>>> stub.mock("temperature", force_property=True).return_value(98)
<chainmock._api.Assert object at ...>
>>> stub.temperature
98
>>> State.teardown() #! hidden

```

## Asserting property access

### Assert read access

You can verify that a property was accessed (read):

```python
>>> mocker(Teapot).mock("state").called_once()
<chainmock._api.Assert object at ...>
>>> teapot = Teapot()
>>> _ = teapot.state  # Access the property
>>> State.teardown() #! hidden

```

Assert that a property was read exactly twice:

```python
>>> mocker(Teapot).mock("state").called_twice()
<chainmock._api.Assert object at ...>
>>> teapot = Teapot()
>>> _ = teapot.state  # First access
>>> _ = teapot.state  # Second access
>>> State.teardown() #! hidden

```

Assert that a property was never accessed:

```python
>>> mocker(Teapot).mock("state").not_called()
<chainmock._api.Assert object at ...>
>>> State.teardown() #! hidden

```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
