# Chainmock

Mocking library for Python and Pytest.

## TODO

- Test spying derived classes
- Support spying async methods and functions
- Patch class and class instance automatically by doing both at the same time?
- Patching and mocking attributes that exist only during runtime?
- Test mocking proxies
- Test spying proxies
- Mocking mangled methods
- Call at_least and at_most modifiers
- Implement match call args method
- Use autospec?
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
