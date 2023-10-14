# Changelog

This project follows semantic versioning.

Types of changes:

- **Added**: New features.
- **Changed**: Changes in existing functionality.
- **Deprecated**: Soon-to-be removed features.
- **Removed**: Removed features.
- **Fixed**: Bug fixes.
- **Infrastructure**: Changes in build or deployment infrastructure.
- **Documentation**: Changes in documentation.

## Unreleased

### Added

- Add `unittest` integration.

### Removed

- Drop support for pytest v6.0 and v6.1.

### Infrastructure

- Add pypy3.10 to tox test run.

## Release 0.8.2

### Changed

- Raise an exception if non-callables are spied.

## Release 0.8.1

### Fixed

- Fix mocks leak to next test if pytest setup fails.

## Release 0.8.0

### Changed

- Set name to unittest mocks for better error messages.
- Raise AttributeError if async asserts called without AsyncMock.

### Fixed

- Fix mocking chained async methods and properties.

## Release 0.7.1

### Added

- Export `mock.AnyOf` helper class.

## Release 0.7.0

### Added

- Use force_property=True always with kwargs.

### Fixed

- Fix spying **init** method fails.

## Release 0.6.0

### Added

- Add support for mocking module variables.
- Add `force_async` parameter to `Mock.mock` method.

## Release 0.5.1

### Added

- Return self when Mock is called directly.

## Release 0.5.0

### Added

- Add `force_property` parameter to `Mock.mock` method.
- Convert kwargs to properties for stubs without a spec.
- Implement property mocking with patching.

### Fixed

- Fix stub assertions not executed.

## Release 0.4.1

### Fixed

- Fix stub properties attached to Mock class.

## Release 0.4.0

### Added

- Support setting properties for stubs with spec.

### Fixed

- Fix stubs are cached.

## Release 0.3.0

### Added

- Implement `Assert.any_await_with` method.
- Implement `Assert.any_call_with` method.
- Implement `Assert.all_awaits_with` method.
- Implement `Assert.all_calls_with` method.
- Implement `Assert.match_args_last_await` method.
- Implement `Assert.match_args_last_call` method.
- Implement `Assert.match_args_any_await` method.
- Implement `Assert.match_args_any_call` method.
- Implement `Assert.match_args_all_awaits` method.
- Implement `Assert.match_args_all_calls` method.
- Implement `Assert.get_mock` method.
- Add ANY_TYPE argument matching helpers.

### Fixed

- Prevent spying or mocking the same attribute twice.
- Fix await count mixed with call count.

## Release 0.2.0

### Added

- Implement spying.
- Add called at least and at most modifiers.
- Support mocking and spying mangled methods.
- Support mocking and spying proxies.
- Support mocking non-existing attributes.
- Support spying async methods and functions.
- Add stdlib re-exports.
- Test Python and Pytest versions using tox.

## Release 0.1.0

Initial release.
