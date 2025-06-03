# Logger Design Specification

## Overview
This Python module provides a robust logging system with configurable settings and thread-safe singleton access. It enables centralized logging with flexible configurations, ensuring streamlined logging across applications.

## Design Components

### Classes:
- **`LoggingService`**: Defines a protocol for retrieving a logger instance.
- **`LoggerConfig`**: Configures and manages logger instances, enforcing standard handlers and logging levels.
- **`SingletonLogger`**: Implements a thread-safe singleton pattern for retrieving a consistent logger instance across threads.

### Methods:
#### `LoggerConfig`
- **`__init__`**: Initializes a logger with name, level, and handlers.
- **`_configure_logger`**: Creates and sets up a logger.
- **`_add_unique_handler`**: Ensures handlers are not duplicated when adding them.
- **`_default_stream_handler`**: Provides a default stream handler with timestamped formatting.

#### `SingletonLogger`
- **`get_logger`**: Provides a thread-safe singleton logger instance.

## Functionality
- Establishes a centralized logging mechanism.
- Ensures thread safety through locking in `SingletonLogger`.
- Prevents duplicate handlers from being added.
- Provides default logging format: `%(asctime)s - %(levelname)s - %(message)s`.

## Example Usage
```python
logger = SingletonLogger.get_logger()
logger.info("Logger successfully initialized!")
