import unittest
import logging
from unittest.mock import patch
from app_logging import LoggerConfig, SingletonLogger


class TestLoggerConfig(unittest.TestCase):
    """Tests for LoggerConfig initialization and behavior."""

    def setUp(self) -> None:
        """Setup runs before each test method."""
        self.logger_config = LoggerConfig(name="test_logger", level=logging.DEBUG)

    def tearDown(self) -> None:
        """Ensure logger handlers are cleared after each test."""
        handlers = list(self.logger_config.logger.handlers)  # Copy list before clearing
        for handler in handlers:
            self.logger_config.logger.removeHandler(handler)

    def test_logger_instance_creation(self) -> None:
        """Ensure logger is correctly instantiated."""
        self.assertIsInstance(self.logger_config.logger, logging.Logger)
        self.assertEqual(self.logger_config.logger.name, "test_logger")

    def test_logger_has_correct_level(self) -> None:
        """Verify the logger level is correctly set."""
        self.assertEqual(self.logger_config.logger.level, logging.DEBUG)

    def test_default_handler_attached(self) -> None:
        """Ensure default StreamHandler is properly assigned."""
        handlers = self.logger_config.logger.handlers
        self.assertTrue(any(isinstance(handler, logging.StreamHandler) for handler in handlers))

    @patch("logging.FileHandler")  # Prevent actual file creation
    def test_add_unique_handler(self, mock_file_handler) -> None:
        """Validate adding a unique handler."""
        test_handler = mock_file_handler.return_value
        self.logger_config._add_unique_handler(self.logger_config.logger, test_handler)
        self.assertIn(test_handler, self.logger_config.logger.handlers)


class TestSingletonLogger(unittest.TestCase):
    """Tests for SingletonLogger behavior."""

    def setUp(self) -> None:
        """Reset Singleton for accurate testing."""
        SingletonLogger._instance = None  # Ensure fresh instance for tests

    def test_singleton_instance(self) -> None:
        """Ensure SingletonLogger maintains a single instance."""
        logger1 = SingletonLogger.get_logger()
        logger2 = SingletonLogger.get_logger()
        self.assertIs(logger1, logger2)

    def test_logger_is_instance_of_logging(self) -> None:
        """Ensure SingletonLogger returns a valid logger instance."""
        logger = SingletonLogger.get_logger()
        self.assertIsInstance(logger, logging.Logger)

    def test_logging_info_message(self) -> None:
        """Validate info-level logging."""
        logger = SingletonLogger.get_logger()
        with self.assertLogs(logger, level="INFO") as log_capture:
            logger.info("Test info message.")
        self.assertTrue(any("INFO" in msg and "Test info message." in msg for msg in log_capture.output))

    def test_logging_exception_handling(self) -> None:
        """Ensure logger properly captures exceptions."""
        logger = SingletonLogger.get_logger()
        try:
            raise ValueError("Test error.")
        except ValueError as e:
            with self.assertLogs(logger, level="ERROR") as log_capture:
                logger.exception("An error occurred!", exc_info=e)
            self.assertTrue(any("ERROR" in msg and "An error occurred!" in msg for msg in log_capture.output))


class TestEdgeCases(unittest.TestCase):
    """Tests edge cases and uncommon scenarios."""

    def test_empty_logger_name(self) -> None:
        """Ensure logger creation succeeds with an empty name."""
        config = LoggerConfig(name="", level=logging.DEBUG)
        self.assertIsInstance(config.logger, logging.Logger)
        self.assertEqual(config.logger.name, "default_logger")  # Use enforced default name

    def test_invalid_logging_level(self) -> None:
        """Ensure improper logging levels default to INFO."""
        config = LoggerConfig(level=9999)  # Invalid level
        self.assertEqual(config.logger.level, logging.INFO)

    def test_logging_with_no_handlers(self) -> None:
        """Ensure logger functions properly even when no handlers are set."""
        config = LoggerConfig(name="test_no_handler", level=logging.WARNING, handlers=[])
        logger = config.logger

        # Ensure the logger does NOT inherit parent handlers
        logger.propagate = False

        # Explicitly remove any existing handlers
        for handler in list(logger.handlers):
            logger.removeHandler(handler)

        self.assertEqual(len(logger.handlers), 0)

    def test_logging_large_message(self) -> None:
        """Ensure large log messages do not crash the system."""
        logger = SingletonLogger.get_logger()
        large_message = "A" * 10000  # Very long message
        with self.assertLogs(logger, level="INFO") as log_capture:
            logger.info(large_message)
        self.assertTrue(any("INFO" in msg and large_message in msg for msg in log_capture.output))

    def test_logging_special_characters(self) -> None:
        """Ensure logging handles special characters gracefully."""
        logger = SingletonLogger.get_logger()
        special_message = "Testing special chars: ☺️🚀🔥"
        with self.assertLogs(logger, level="INFO") as log_capture:
            logger.info(special_message)
        self.assertTrue(any("INFO" in msg and special_message in msg for msg in log_capture.output))

    def test_exception_logging_with_invalid_exception(self) -> None:
        """Ensure logging exception handles None-type properly."""
        logger = SingletonLogger.get_logger()
        with self.assertLogs(logger, level="ERROR") as log_capture:
            try:
                raise ValueError("Sample exception")
            except ValueError:
                logger.exception("Handling exception", exc_info=None)  # Passing None intentionally
        self.assertTrue(any("ERROR" in msg and "Handling exception" in msg for msg in log_capture.output))


if __name__ == "__main__":
    unittest.main()
