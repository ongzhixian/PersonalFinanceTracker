

# App Configuration Design Specification

## Overview
This Python module provides a thread-safe singleton-based configuration management system for applications. It enables loading, validating, and retrieving configuration data from a JSON file or a raw dictionary. The system ensures safe concurrent access to configuration settings.

## Architecture
The design consists of three primary components:
1. **`SingletonMeta`** - A thread-safe singleton metaclass using weak references.
2. **`ConfigLoader`** - Handles loading, validation, and deep-copy retrieval of configuration from JSON or raw dictionary.
3. **`AppConfiguration`** - Singleton class providing application-wide access to configuration in a thread-safe manner.

---

## Classes & Methods

### `ConfigurationError(Exception)`
Raised when a configuration-related issue occurs.

### `SingletonMeta(type)`
Thread-safe singleton metaclass using weak references.
- **`__call__(cls, *args, **kwargs) -> Any`**: Ensures only one instance of a class exists.
- **`reset_instance(cls) -> None`**: Resets the singleton instance, useful for testing.

### `ConfigLoader`
Handles safe loading and validation of configuration from a JSON file or raw dictionary.
- **`__init__(self, file_path: Optional[str] = None, raw_config: Optional[Dict[str, Any]] = None) -> None`**: Initializes configuration from a JSON file or raw dictionary.
- **`_validate_config(self, config: Any) -> Dict[str, Any]`**: Validates that configuration data is a dictionary.
- **`reload(self) -> None`**: Reloads configuration from a JSON file.
- **`config(self) -> Dict[str, Any]`**: Provides a deep copy of the current configuration.

### `AppConfiguration(SingletonMeta)`
Singleton class for managing application configuration in a thread-safe manner.
- **`__init__(self, configuration_json_file_path: Optional[str] = None, raw_config: Optional[Dict[str, Any]] = None) -> None`**: Initializes the configuration from a file or dictionary.
- **`reload(self) -> None`**: Reloads the configuration file or resets stored configuration.
- **`get(self, path: str, default: Optional[T] = None, raise_on_missing: bool = False) -> Optional[T]`**: Retrieves a configuration value using a colon-separated path.
- **`contains(self, path: str) -> bool`**: Checks if a configuration key exists.
- **`reset_instance(cls) -> None`**: Resets the singleton instance.

---

## Key Features
- **Thread-Safe Singleton**: Ensures only one instance is created and prevents data inconsistencies.
- **JSON & Dictionary Support**: Accepts configuration data from a file or raw dictionary.
- **Deep Copy Retrieval**: Prevents unintended mutations of configuration data.
- **Graceful Error Handling**: Handles issues like missing files, invalid JSON, and incorrect configurations.
- **Scoped Key Access**: Enables retrieving nested values with a colon-separated key path.
