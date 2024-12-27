# Stubs

If `mocker` is invoked without a target, it creates a stub, an empty object that doesn't have any methods or attributes. For example, by calling `mocker()`. You can then explicitly set these methods and attributes as needed during testing. This is useful for simulating behavior within your test environment, ensuring that your code interacts as expected with the stubbed object.

If `mocker` is invoked without a target, a stub is created. For example, by calling `mocker()`. The created stub doesn't have any methods or attributes until you explicitly set them.

Create a _stub_ and attach methods to it:

```python
#! remove-prefix
>>> stub = mocker()
>>> stub.mock("my_method").return_value("It works!")
<chainmock._api.Assert object at ...>
>>> stub.mock("another_method").side_effect(RuntimeError("Oh no!"))
<chainmock._api.Assert object at ...>
>>> assert stub.my_method() == "It works!"
>>> stub.another_method()
Traceback (most recent call last):
  ...
RuntimeError: Oh no!
>>> State.teardown() #! hidden

```

There is also a shorthand for creating a stub and attaching attributes and methods to it by passing keyword arguments to `mocker`. The keyword arguments are used to set the attributes and methods of the stub.

```python
#! remove-prefix
>>> stub = mocker(my_method=lambda: "It works!", property="value")
>>> assert stub.my_method() == "It works!"
>>> assert stub.property == "value"
>>> State.teardown() #! hidden

```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
