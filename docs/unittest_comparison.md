# Comparison with unittest.mock

Chainmock is built on top of Python's `unittest.mock` but provides a more intuitive and streamlined interface. Here are some key advantages of using Chainmock:

- **Automatic teardown**: Chainmock handles mock cleanup automatically at the end of each test.
- **Lazy evaluation**: Assertions are evaluated during teardown, not immediately when called.
- **Method chaining**: Multiple assertions can be chained together in a single line.
- **Less boilerplate**: More concise syntax for common mocking patterns.

Chainmock also provides some additional features not available in `unittest.mock`, such as:

- [Partial argument matching](./user_guide/argument_matching.md).
- More granular call count assertions (e.g., `call_count_at_least`, `call_count_at_most`).
- Spying without mocking which is not directly supported by `unittest.mock`.

Let's look at some practical examples comparing `unittest.mock` and Chainmock approaches.

## Basic mocking and assertions

### Mocking a method return value

With unittest:

```python
#! remove-prefix
>>> from unittest import mock #! hidden
>>> teapot = Teapot()
>>> with mock.patch.object(teapot, 'add_tea') as mocked:
...     mocked.return_value = 'mocked'
...     assert teapot.add_tea('green') == 'mocked'
...     mocked.assert_called_once_with('green')

```

With Chainmock:

```python
#! remove-prefix
>>> teapot = Teapot()
>>> mocker(teapot).mock('add_tea').return_value('mocked').called_once_with('green')
<chainmock._api.Assert object at ...>
>>> assert teapot.add_tea('green') == 'mocked'

```

## Side effects and exceptions

### Raising exceptions

With unittest:

```python
#! remove-prefix
>>> teapot = Teapot()
>>> with mock.patch.object(teapot, 'brew') as mocked:
...     mocked.side_effect = ValueError("No tea!")
...     try:
...         teapot.brew()
...     except ValueError as e:
...         assert str(e) == "No tea!"
...     mocked.assert_called_once()

```

With Chainmock:

```python
#! remove-prefix
>>> teapot = Teapot()
>>> mocker(teapot).mock('brew').side_effect(ValueError("No tea!")).called_once()
<chainmock._api.Assert object at ...>
>>> try:
...     teapot.brew()
... except ValueError as e:
...     assert str(e) == "No tea!"

```

### Sequential return values

With unittest:

```python
#! remove-prefix
>>> teapot = Teapot()
>>> with mock.patch.object(teapot, 'fill') as mock_fill:
...     mock_fill.side_effect = ['full', 'overfull', 'spilling']
...     assert teapot.fill() == 'full'
...     assert teapot.fill() == 'overfull'
...     assert teapot.fill() == 'spilling'
...     assert mock_fill.call_count == 3

```

With Chainmock:

```python
#! remove-prefix
>>> teapot = Teapot()
>>> mocker(teapot).mock("fill").side_effect(
...     ["full", "overfull", "spilling"]
... ).call_count(3)
<chainmock._api.Assert object at ...>
>>> assert teapot.fill() == 'full'
>>> assert teapot.fill() == 'overfull'
>>> assert teapot.fill() == 'spilling'

```

## Stubs

### Stubbing attributes

With unittest:

```python
#! remove-prefix
>>> stub = mock.Mock()
>>> stub.attribute = 'value'
>>> stub.other_attribute = 'other_value'
>>> assert stub.attribute == 'value'
>>> assert stub.other_attribute == 'other_value'

```

With Chainmock:

```python
#! remove-prefix
>>> stub = mocker(attribute='value', other_attribute='other_value')
>>> assert stub.attribute == 'value'
>>> assert stub.other_attribute == 'other_value'

```

### Stubbing methods

With unittest:

```python
#! remove-prefix
>>> stub = mock.Mock()
>>> stub.method.return_value = 'mocked'
>>> assert stub.method() == 'mocked'

```

With Chainmock:

```python
#! remove-prefix
>>> stub = mocker(method=lambda: 'mocked')
>>> assert stub.method() == 'mocked'

```
