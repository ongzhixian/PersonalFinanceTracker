Given:

```app_configuration.json
{
  "application": {
    "name": "TEST_APP",
    "version": "1.0.1"
  },
  "booking_settings": {
    "booking_id_prefix": "BK"
  },
  "seat_statuses": {
    "available": "O",
    "booked": "B",
    "proposed": "P"
  },
  "seat_status_symbols": {
    "AVAILABLE": ".",
    "BOOKED": "#",
    "PROPOSED": "P"
  },
  "database_settings": {
    "seating_planner": {
      "type": "sqlite",
      "file_path": "seating_planner.db"
    }
  }
}
```

```app_configuration.py
import json
import threading
from typing import Any, Dict, Optional, TypeVar, Type

T = TypeVar('T')

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class SingletonMeta(type):
    """Thread-safe Singleton metaclass."""
    _instances: Dict[Type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
            return cls._instances[cls]

    def reset_instance(cls) -> None:
        """Resets the singleton instance (useful for testing)."""
        with cls._lock:
            cls._instances.pop(cls, None)


class ConfigLoader:
    """Handles loading and reloading configuration from a JSON file."""

    def __init__(self, file_path: str) -> None:
        self._file_path: str = file_path
        self._lock: threading.RLock = threading.RLock()
        self._config: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Reload configuration data from JSON file."""
        with self._lock:
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                if not isinstance(config, dict):
                    raise ConfigurationError("Configuration root must be a dictionary.")
                self._config = config
            except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
                raise ConfigurationError(f"Error loading configuration file: {e}") from e

    @property
    def config(self) -> Dict[str, Any]:
        """Returns a copy of the current configuration."""
        with self._lock:
            return self._config.copy()

class AppConfiguration(metaclass=SingletonMeta):
    """
    Thread-safe Singleton for application configuration.
    Supports nested key retrieval via colon-separated paths.
    """

    def __init__(self, configuration_json_file_path: str) -> None:
        self._loader: ConfigLoader = ConfigLoader(configuration_json_file_path)
        self._lock: threading.RLock = threading.RLock()

    def reload(self) -> None:
        """Reload the configuration from the file."""
        self._loader.reload()

    def get(self, path: str, default: Optional[T] = None, raise_on_missing: bool = False) -> Optional[T]:
        """
        Retrieve a configuration value using a colon-separated path for nested values.

        Args:
            path (str): Colon-separated path string (e.g., "booking_settings:booking_id_prefix").
            default (Any, optional): Value to return if key is not found.
            raise_on_missing (bool): If True, raise ConfigurationError if key is missing.

        Returns:
            Any: The configuration value, or default if not found.
        """
        with self._lock:
            keys = path.split(":")
            value: Any = self._loader.config
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

    def contains(self, path: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            path (str): Colon-separated path string.

        Returns:
            bool: True if key exists, False otherwise.
        """
        try:
            self.get(path, raise_on_missing=True)
            return True
        except ConfigurationError:
            return False

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing purposes)."""
        SingletonMeta.reset_instance(cls)

# Example usage:
if __name__ == '__main__':
    config = AppConfiguration("app_configuration.json")
    value = config.get("booking_settings:booking_id_prefix", default="default_value")
    print(value)
```

You are an extremely picky code reviewer.
Review code and provide a fully refactored and optimized code.
Refactored code should not need further changes should you review it again.

Code should follow best practices.
Code should use design patterns whenever possible.
Code should have typing and follow SOLID principles.
Code should be easily testable using unittest.
Prioritize readability and maintainability.
Identify illogical constructs and poor names if any.
Add any missing error handling.
Add any missing docstrings.


2
Refactored code should not need further changes should you review it again.