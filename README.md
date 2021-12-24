# Chainmock

Mocking library for Python and Pytest.

## TODO

- Unclear error message when call arguments not mathed:
  - AssertionError: Expected 'class_method_with_args' to have been called twice. Called 1 times.
  - any_call_with: does not print call list.
- Patching and mocking attributes that exist only during runtime?
- Reimports from unittest
- Print await_args_list with await args error messages

- Test mocking proxies
- Mocking mangled methods
- Call at_least and at_most modifiers
- Implement match call args method
- Implement spying
- Use autospec?
- Add tox tests
- Update docstrings
- Create documentation
- Test with doctest
- Add examples
- Better type hint for side_effect value?
- Test calling await functions with non-async functions and vice-versa
- Add methods to Assert:
  - await_count
  - await_args
  - await_args_list
  - call_count
  - call_args (-> last_call_args)
  - call_args_list
  - method_calls?
  - mock_calls?
- NonCallableMock for non-callable mocking?
- Update project information in pyproject.toml
