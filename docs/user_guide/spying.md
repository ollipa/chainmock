# Spying

Spying allows monitoring specific interactions with objects or methods in your code. When you create a spy, you essentially "watch" the behavior of the target object or method, without changing its original functionality. With spies, you can assert that a function or method was called without mocking it.

Assert that the method `add_tea` was called once:

```python
#! remove-prefix
>>> teapot = Teapot()
>>> assert teapot.add_tea("white tea") == "loose white tea"
>>> mocker(teapot).spy("add_tea").called_once()
<chainmock._api.Assert object at ...>
>>> assert teapot.add_tea("white tea") == "loose white tea"
>>> State.teardown() #! hidden

```

Assert that the method add_tea was called with specific arguments:

```python
#! remove-prefix
>>> teapot = Teapot()
>>> assert teapot.add_tea("white tea", loose=False) == "bagged white tea"
>>> mocker(teapot).spy("add_tea").called_last_with("green tea", loose=True)
<chainmock._api.Assert object at ...>
>>> assert teapot.add_tea("green tea", loose=True) == 'loose green tea'
>>> State.teardown() #! hidden

```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
