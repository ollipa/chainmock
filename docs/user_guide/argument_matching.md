# Partial argument matching

Chainmock provides several methods for matching argument in function calls and awaits. These methods are more flexible than exact matching methods, as they allow you to match specific arguments without caring about others.

The `match_args_*` methods are more flexible than their exact matching counterparts:

- They only check for the presence of specified arguments, ignoring any additional arguments.
- You can match just positional arguments, just keyword arguments, or both.
- The order of positional arguments matters, but unspecified arguments are ignored.
- Perfect for cases where you only care about specific arguments being present.

Compare these approaches:

```python
# Exact matching - this will fail because it expects exact arguments
>>> teapot = Teapot()
>>> mocker(teapot).mock("add_tea").called_last_with("green")
<chainmock._api.Assert object at ...>
>>> teapot.add_tea("green", loose=False)  # This fails the exact match
>>> State.teardown() #! hidden
Traceback (most recent call last):
  ...
AssertionError: expected call not found.
Expected: Teapot.add_tea('green')
Actual: Teapot.add_tea('green', loose=False)

```

```python
# Argument matching - this will pass because it only checks for "green"
>>> teapot = Teapot()
>>> mocker(teapot).mock("add_tea").match_args_last_call("green")
<chainmock._api.Assert object at ...>
>>> teapot.add_tea("green", loose=False)  # This passes the argument match
>>> State.teardown() #! hidden

```

There are multiple matching methods available that allow you to match arguments in different ways:

- Match arguments in all calls to the mocked function.
  - All calls must match the specified arguments.
- Match arguments to any call to the mocked function.
  - At least one call must match the specified arguments.
- Match arguments in the last call to the mocked function.

There also exists async versions of these methods that will check for arguments in awaits instead of calls.

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
