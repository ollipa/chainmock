<h1 align="center">Chainmock</h1>

<p align="center">
<a href="https://pypi.org/project/chainmock/">
  <img src="https://img.shields.io/pypi/v/chainmock" alt="pypi">
</a>
<a href="https://github.com/ollipa/chainmock/actions/workflows/ci.yml">
  <img src="https://github.com/ollipa/chainmock/actions/workflows/ci.yml/badge.svg" alt="ci">
</a>
<a href="https://chainmock.readthedocs.io/">
  <img src="https://img.shields.io/readthedocs/chainmock" alt="documentation">
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/pypi/l/chainmock" alt="license">
</a>
</p>

<hr>

Mocking library for Python and Pytest.

Chainmock is a wrapper for Python unittest unit testing library. It provides an
alternative syntax to create mocks and assertions and adds some additional
features to make testing fast and straightforward. The syntax works especially
well with pytest fixtures and it makes the tests easy to read.

**Documentation**: https://chainmock.readthedocs.io/

## Installation

Install with pip:

```
pip install chainmock
```

## Features

Chainmock supports all the same features that Python standard library unittest
supports and adds some convenient extra functionality.

- **Mocking**: Create _mocks_ and assert call counts and arguments or replace
  return values.
- **Spying**: _Spying_ proxies the calls to the original function or method and
  you can assert call counts and arguments.
- **Stubs**: Easily create _stub_ objects that can be used in tests as fake data
  or to replace real objects.
- **Async support**: Chainmock supports mocking and spying _async_ functions and
  methods. Most of the time it also automatically recognizes when async mocking
  should be used so is not any harded than mocking sync code.
- **Fully type annotated**: The whole codebase is fully type annotated so
  Chainmock works well with editor auto completion and static analysis tools.
- Works with **Python 3.8+ and PyPy3**.

## Examples

The entrypoint to Chainmock is the `mocker` function. Import the `mocker`
as follows:

```python
from chainmock import mocker
```

### Mocking

To mock you just give the object that you want to mock to the `mocker` function.
After this you can start mocking individual attributes and methods as follows:

```python
# Assert that a certain method has been called exactly once
mocker(Teapot).mock("add_tea").called_once()

# Provide a return value and assert that method has been called twice
mocker(Teapot).mock("brew").return_value("mocked").called_twice()

# Assert that a method has been called with specific arguments at most twice
mocker(Teapot).mock("add_tea").all_calls_with("green").call_count_at_most(2)
```

### Spying

Spying is easy with Chainmock. You just need to call `spy` instead of `mock`.
After spying a method, the method works just like before, but you can assert
call count and check if it was called with specific arguments.

```python
# Assert that a certain method has been called at least once
mocker(Teapot).spy("add_tea").called()

# Check that a method has been called at least once with the given arguments
mocker(Teapot).spy("add_tea").any_call_with("green").call_count_at_most(2)
```

### Stubs

To create a stub object, just call `mocker` function without any arguments.

```python
# Create a stub with a method called "my_method"
stub = mocker().mock("my_method").return_value("it works!").self()
assert stub.my_method() == "it works!"

# You can give keyword arguments the mocker function to quickly set properties
stub = mocker(my_property=10)
assert stub.my_property == 10
```

For more details and examples, see the documentation.

## Contributing

Do you like this project and want to help? If you need ideas, check out the open issues and feel free to open a new pull request. Bug reports and feature requests are also very welcome.
