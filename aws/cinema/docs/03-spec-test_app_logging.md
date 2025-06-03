# Test Specification: `test_app_logging.py`

## Summary
This module unit tests for validating the behavior of a logging system implemented through `LoggerConfig` and `SingletonLogger`. It ensures that loggers are correctly instantiated, configured, and handle edge cases properly.

## Classes and Methods

### `TestLoggerConfig`
Tests the initialization and functionality of the `LoggerConfig` class.
- `setUp()`: Initializes a test logger before each test.
- `tearDown()`: Cleans up logger handlers after each test.
- `test_logger_instance_creation()`: Validates that a logger instance is created correctly.
- `test_logger_has_correct_level()`: Ensures the logger level is properly assigned.
- `test_default_handler_attached()`: Verifies that a default StreamHandler is assigned.
- `test_add_unique_handler(mock_file_handler)`: Ensures a unique handler is added correctly.

### `TestSingletonLogger`
Verifies the singleton behavior of `SingletonLogger`.
- `setUp()`: Resets the Singleton instance before each test.
- `test_singleton_instance()`: Checks that only one instance of the singleton logger exists.
- `test_logger_is_instance_of_logging()`: Validates that the logger is a valid instance.
- `test_logging_info_message()`: Confirms that info-level messages are logged correctly.
- `test_logging_exception_handling()`: Ensures exception logging works properly.

### `TestEdgeCases`
Tests uncommon scenarios and edge cases in logging.
- `test_empty_logger_name()`: Verifies that an empty logger name defaults correctly.
- `test_invalid_logging_level()`: Ensures invalid logging levels default to INFO.
- `test_logging_with_no_handlers()`: Checks behavior when no handlers are attached.
- `test_logging_large_message()`: Ensures large log messages do not cause crashes.
- `test_logging_special_characters()`: Validates logging of special characters.
- `test_exception_logging_with_invalid_exception()`: Ensures exceptions are logged properly even when `exc_info` is `None`.

## Execution
The script is executed via `unittest.main()`, running all defined tests.

