import logging
import threading
from typing import Optional, Protocol, List


class ILoggingService(Protocol):
    """Protocol defining a logging service for dependency injection."""

    def get_logger(self) -> logging.Logger:
        """Retrieves a logger instance."""


class LoggerConfig:
    """Handles logger configuration with extendable handlers."""

    def __init__(self, name: str = "app_logger", level: int = logging.INFO, handlers: Optional[List[logging.Handler]] = None):
        """
        Initializes the logger configuration.

        Args:
            name (str): Logger name.
            level (int): Logging level.
            handlers (Optional[List[logging.Handler]]): List of handlers.
        """
        self.name = name
        self.level = level
        self.handlers = handlers or [self._create_stream_handler()]
        self.logger = self._configure_logger()

    def _configure_logger(self) -> logging.Logger:
        """Creates and configures a logger instance."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)

        if not logger.hasHandlers():
            for handler in self.handlers:
                self._add_handler_if_not_exists(logger, handler)

        return logger

    @staticmethod
    def _add_handler_if_not_exists(logger: logging.Logger, handler: logging.Handler) -> None:
        """Adds a handler to the logger if it doesn't already exist."""
        if all(not isinstance(existing_handler, type(handler)) for existing_handler in logger.handlers):
            logger.addHandler(handler)

    @staticmethod
    def _create_stream_handler() -> logging.StreamHandler:
        """Creates a StreamHandler with standardized formatting."""
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        return handler


class AppLogger(ILoggingService):
    """Thread-safe Singleton Logger."""

    _instance: Optional[logging.Logger] = None
    _singleton_lock = threading.Lock()

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Retrieves the singleton logger instance."""
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:  # Ensures only one instance is created
                    cls._instance = LoggerConfig().logger

        return cls._instance


# Example Usage
if __name__ == "__main__":
    logger = AppLogger.get_logger()
    try:
        logger.info("Logger is configured and running!")
    except Exception as e:
        logger.error(f"Logging failed: {e}")

