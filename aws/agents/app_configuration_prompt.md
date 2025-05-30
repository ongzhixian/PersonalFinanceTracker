Given:

```app_configuration.json
{
  "application": {
    "name": "SOME APPLICATION NAME",
    "version": "1.0.1"
  },
  "booking_settings": {
    "booking_id_prefix": "BK"
  },
  "databases": {
    "seating_planner": {
      "type": "sqlite",
      "file_path": "seating_planner.db"
    }
  }
}
```

```app_configuration.py
# app_configuration.py

import json
import threading
from typing import Any, Dict, Optional, TypeVar, Generic, Type

T = TypeVar('T')

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass

class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass.
    """
    _instances: Dict[Type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

    def reset_instance(cls):
        with cls._lock:
            if cls in cls._instances:
                del cls._instances[cls]

class AppConfiguration(metaclass=SingletonMeta):
    """
    Thread-safe Singleton for application configuration.
    Supports nested key retrieval via colon-separated strings.
    """

    def __init__(self, configuration_json_file_path: str) -> None:
        self._lock = threading.RLock()
        self._config: Dict[str, Any] = {}
        self._file_path = configuration_json_file_path
        self.reload()

    def reload(self) -> None:
        """
        Reload the configuration from the file.
        """
        with self._lock:
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                if not isinstance(config, dict):
                    raise ConfigurationError("Configuration root must be a dictionary.")
                self._config = config
            except FileNotFoundError as e:
                raise ConfigurationError(f"Configuration file not found: {self._file_path}") from e
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in configuration file: {e}") from e

    def get_value(self, path: str, default: Optional[T] = None, raise_on_missing: bool = False) -> Optional[T]:
        """
        Retrieve a configuration value using a colon-separated path for nested values.

        Args:
            path (str): Colon-separated path string, e.g., "booking_settings:booking_id_prefix"
            default (Any, optional): Value to return if key is not found.
            raise_on_missing (bool): If True, raise ConfigurationError if key is not found.

        Returns:
            Any: The configuration value, or default if not found.
        """
        with self._lock:
            keys = path.split(":")
            value: Any = self._config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                elif isinstance(value, list) and key.isdigit():
                    idx = int(key)
                    if 0 <= idx < len(value):
                        value = value[idx]
                    else:
                        if raise_on_missing:
                            raise ConfigurationError(f"Index '{key}' out of range for path '{path}'")
                        return default
                else:
                    if raise_on_missing:
                        raise ConfigurationError(f"Key '{key}' not found in path '{path}'")
                    return default
            return value

    def has_key(self, path: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            path (str): Colon-separated path string.

        Returns:
            bool: True if key exists, False otherwise.
        """
        try:
            self.get_value(path, raise_on_missing=True)
            return True
        except ConfigurationError:
            return False

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing purposes).
        """
        SingletonMeta.reset_instance(cls)

# Example usage:
if __name__ == '__main__':
    config = AppConfiguration("app_configuration.json")
    value = config.get_value("booking_settings:booking_id_prefix", default="default_value")
    print(value)
```

Perform a code review to refactor code.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.
