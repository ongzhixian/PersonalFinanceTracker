Given the following Python code:

```app_configuration.py
import json
import threading
import weakref
from typing import Any, Dict, Optional, TypeVar, Type

T = TypeVar('T')


class ConfigurationError(Exception):
    """Raised when a configuration-related issue occurs."""
    pass


class SingletonMeta(type):
    """Thread-safe Singleton metaclass using weak references."""

    _instances: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

    def reset_instance(cls) -> None:
        """Resets the singleton instance for testing."""
        with cls._lock:
            cls._instances.pop(cls, None)


class ConfigLoader:
    """Handles safe loading and validation of configuration from a JSON file."""

    def __init__(self, file_path: Optional[str] = None, raw_config: Optional[Dict[str, Any]] = None) -> None:
        self._lock: threading.RLock = threading.RLock()
        self._config: Dict[str, Any] = {}

        if raw_config is not None:
            self._config = self._validate_config(raw_config)
        elif file_path:
            self._file_path = file_path
            self.reload()

    def _validate_config(self, config: Any) -> Dict[str, Any]:
        """Ensures that the configuration is a valid dictionary."""
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration root must be a dictionary.")
        return config

    def reload(self) -> None:
        """Reloads configuration from a JSON file."""
        with self._lock:
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self._config = self._validate_config(config)
            except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
                raise ConfigurationError(f"Error loading configuration file: {e}") from e

    @property
    def config(self) -> Dict[str, Any]:
        """Returns a deep copy of the current configuration."""
        with self._lock:
            return json.loads(json.dumps(self._config))  # Deep copy to prevent mutations


class AppConfiguration(metaclass=SingletonMeta):
    """
    Singleton class for accessing application configuration in a thread-safe manner.
    """

    def __init__(self, configuration_json_file_path: Optional[str] = None,
                 raw_config: Optional[Dict[str, Any]] = None) -> None:
        if configuration_json_file_path:
            self._loader = ConfigLoader(file_path=configuration_json_file_path)
        elif raw_config:
            self._loader = ConfigLoader(raw_config=raw_config)
        else:
            raise ConfigurationError("Either a file path or raw configuration must be provided.")
        self._lock: threading.RLock = threading.RLock()

    def reload(self) -> None:
        """Reload the configuration file or reset configuration."""
        with self._lock:
            if hasattr(self._loader, "_file_path"):
                self._loader.reload()  # Reload from file
            else:
                raise ConfigurationError("Reload cannot be used when raw config is provided.")

    def get(self, path: str, default: Optional[T] = None, raise_on_missing: bool = False) -> Optional[T]:
        """
        Retrieve a configuration value using a colon-separated path.

        Args:
            path (str): Colon-separated path string (e.g., "booking_settings:booking_id_prefix").
            default (Any, optional): Value to return if key is not found.
            raise_on_missing (bool): If True, raises ConfigurationError if key is missing.

        Returns:
            Any: The configuration value, or default if not found.
        """
        with self._lock:
            keys = path.split(":")
            value: Any = self._loader.config

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
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
        return self.get(path, raise_on_missing=False) is not None

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance."""
        SingletonMeta.reset_instance(cls)

```

```shared_data_models.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any

from app_configuration import AppConfiguration


class MenuOption(Enum):
    BOOK_SEATS = auto()
    VIEW_BOOKING = auto()
    EXIT = auto()


class SeatStatus:
    """
    Encapsulates seat status codes, loaded from configuration.
    """
    AVAILABLE: str = "O"
    BOOKED: str = "B"
    PROPOSED: str = "P"

    @staticmethod
    def from_config(config: AppConfiguration) -> "SeatStatus":
        statuses: Dict[str, Any] = config.get("seat_statuses", {})
        status = SeatStatus()
        status.AVAILABLE = statuses.get("available", "O")
        status.BOOKED = statuses.get("booked", "B")
        status.PROPOSED = statuses.get("proposed", "P")
        return status


@dataclass(frozen=True)
class Seat:
    """
    Represents a single seat in the seating plan.
    """
    row: int
    col: int
    status: str


@dataclass(frozen=True)
class SeatingPlan:
    """
    Represents the complete seating plan with a title and the seat statuses.
    Includes the number of available seats.
    """
    title: str
    plan: List[List[Seat]]
    available_seats_count: int
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

Focus on shared_data_models.py