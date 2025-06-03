# Test Specification for `test_app_configuration.py`

## Summary
This module unit tests for the `AppConfiguration` class using Python's `unittest` framework. It validates configuration retrieval, singleton behavior, and expected failures when reloading raw configurations.

## Classes and Methods

### `TestAppConfiguration`
This test class verifies the correctness of the `AppConfiguration` class.

- **`setUp()`**: Resets the singleton instance and initializes a sample configuration for testing.
- **`test_get_existing_key()`**: Tests that an existing configuration key returns the expected value.
- **`test_get_missing_key()`**: Ensures missing keys return `None`.
- **`test_contains_existing_key()`**: Checks if an existing key is correctly identified.
- **`test_contains_missing_key()`**: Validates that a missing key is correctly reported as absent.
- **`test_reload_with_raw_config_fails()`**: Ensures that reloading with raw config raises a `ConfigurationError`.
- **`test_reset_instance()`**: Confirms singleton reset and initialization of a new instance works properly.
- **`test_config_default_behavior()`**: Tests that missing `seat_statuses` key defaults to an empty dictionary.

## Expected Behavior
- The `AppConfiguration` class is singleton-based.
- Configuration keys can be queried via `get()`.
- Presence of keys can be checked using `contains()`.
- Reloading a raw configuration raises an error.
- Resetting the singleton allows the creation of a new instance with a different configuration.
- Default behavior for missing keys ensures safe retrieval with an expected fallback value.

## Notes
This test suite provides coverage for essential configuration management functionalities, ensuring robustness against improper usage or missing configurations.
