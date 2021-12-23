# Chainmock

Mocking library for Python and Pytest.

## TODO

### Before release

- Unclear error message when call arguments not mathed:
  - AssertionError: Expected 'class_method_with_args' to have been called twice. Called 1 times.
- Patching and mocking attributes that exist only during runtime?
- Reimports from unittest

### Later

- Test mocking proxies
- Mocking mangled methods
- Call at_least and at_most modifiers
- Implement match call args method
- Implement spying
- Use autospec?
- Add tox tests
