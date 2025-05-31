import logging
import threading
from typing import Optional, Protocol, List


class LoggingService(Protocol):
    """Protocol defining the structure of a logging service."""

    def get_logger(self) -> logging.Logger:
        """Retrieves a logger instance."""


class LoggerConfig:
    """Handles the configuration and management of logger instances."""

    VALID_LEVELS = {logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL}

    def __init__(self, name: str = "app_logger", level: int = logging.INFO, handlers: Optional[List[logging.Handler]] = None) -> None:
        """
        Initializes the logger configuration.

        Args:
            name (str): Name of the logger.
            level (int): Logging level.
            handlers (Optional[List[logging.Handler]]): List of logging handlers.
        """
        self.name: str = name if name.strip() else "default_logger"  # ✅ Enforce a default name if empty
        self.level: int = level if level in self.VALID_LEVELS else logging.INFO
        self.handlers: List[logging.Handler] = handlers or [self._default_stream_handler()]
        self.logger: logging.Logger = self._configure_logger()

    def _configure_logger(self) -> logging.Logger:
        """Creates and configures the logger instance."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)

        if not logger.handlers:
            for handler in self.handlers:
                self._add_unique_handler(logger, handler)

        return logger

    @staticmethod
    def _add_unique_handler(logger: logging.Logger, handler: logging.Handler) -> None:
        """
        Adds a handler to the logger if it's not already added.

        Args:
            logger (logging.Logger): Logger instance.
            handler (logging.Handler): Logging handler to add.
        """
        if not any(isinstance(existing_handler, type(handler)) for existing_handler in logger.handlers):
            logger.addHandler(handler)

    @staticmethod
    def _default_stream_handler() -> logging.StreamHandler:
        """Creates a default StreamHandler with standardized formatting."""
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        return handler


class SingletonLogger(LoggingService):
    """Singleton Logger with thread safety."""

    _instance: Optional[logging.Logger] = None
    _lock = threading.Lock()

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Retrieves the singleton logger instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Ensures only one instance is created
                    cls._instance = LoggerConfig().logger

        return cls._instance


# Example Usage
if __name__ == "__main__":
    logger = SingletonLogger.get_logger()

    try:
        logger.info("Logger successfully initialized!")
    except Exception as error:
        logger.exception("Unexpected logging failure", exc_info=error)
