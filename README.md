<p align="center">
  <img alt="chainmock" src="https://github.com/ollipa/chainmock/assets/25169984/ad243761-b2ed-4aff-89e7-699e2b4a7e6d">
</p>

<p align="center"><strong>Chainmock</strong> <em>- Mocking library for Python and Pytest.</em></p>

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

<p align="center">
<a href="https://chainmock.readthedocs.io/">
  <b>Documentation</b>
</a>
</p>

<hr>

Chainmock is a mocking Library for Python and pytest. Under the hood it uses Python standard library mocks providing an alternative syntax to create mocks and assertions. Chainmock also comes with some additional features to make testing faster and more straightforward. The syntax works especially well with pytest fixtures.

## Installation

Install with pip:

```
pip install chainmock
```

## Features

Chainmock supports all the same features that Python standard library unittest
mocks support and adds some convenient extra functionality.

- **Mocking**: Create _mocks_ and assert call counts and arguments or replace
  return values.
- **Spying**: _Spying_ proxies the calls to the original function or method.
  With spying you can assert call counts and arguments without mocking.
- **Stubs**: Easily create _stub_ objects that can be used in tests as fake data
  or to replace real objects.
- **Async support**: Chainmock supports mocking and spying _async_ functions and
  methods. Most of the time it also recognizes automatically when async mocking
  should be used so it is not any harder than mocking sync code.
- **Fully type annotated**: The whole codebase is fully type annotated so
  Chainmock works well with static analysis tools and editor autocomplete.
- Works with **Python 3.8+ and PyPy3**.
- Supports `pytest`, `unittest`, and `doctest` test runners.

## Examples

The entrypoint to Chainmock is the `mocker` function. Import the `mocker`
function as follows:

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

Spying is not any harder than mocking. You just need to call the `spy` method
instead of the `mock` method. After spying a callable, it works just like before
spying and you can start making assertions on it.

```python
# Assert that a certain method has been called at least once
mocker(Teapot).spy("add_tea").called()

# Check that a method has been called at most twice and has
# at least one call with the given argument
mocker(Teapot).spy("add_tea").any_call_with("green").call_count_at_most(2)
```

### Stubs

To create a stub object, just call `mocker` function without any arguments.

```python
# Create a stub with a method called "my_method"
stub = mocker().mock("my_method").return_value("it works!").self()
assert stub.my_method() == "it works!"

# You can give keyword arguments to the mocker function to quickly set properties
stub = mocker(my_property=10)
assert stub.my_property == 10
```

For more details and examples, see the [API reference](https://chainmock.readthedocs.io/en/latest/api_reference/).

## Similar projects

If chainmock is not what you need, check out also these cool projects:

- [flexmock](https://github.com/flexmock/flexmock): Chainmock's API is heavily
  inspired by flexmock. Flexmock doesn't use standard library unittest and it
  has fully custom mocking implementation. Compared to flexmock, chainmock has
  more familiar API if you have been using standard library unittest and
  Chainmock also supports async mocking and partial argument matching.
- [pytest-mock](https://github.com/pytest-dev/pytest-mock/): Similar to
  chainmock, pytest-mock is a wrapper for standard library unittest. However,
  pytest-mock doesn't provide any extra functionality as it just exposes
  unittest mocks directly to the user.

## Contributing

Do you like this project and want to help? If you need ideas, check out the open issues and feel free to open a new pull request. Bug reports and feature requests are also very welcome.
