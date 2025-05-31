# Overview

Design document for this application.

# Files / Modules

app_configuration.py
app_logging.py

console_ui.py
fastapi_main.py
main.py

seating_planner.py
shared_data_models.py

test_app_configuration.py
test_app_logging.py



# File: app_configuration.py

ConfigurationError: Custom exception for configuration-related errors.

SingletonMeta: A metaclass implementing a thread-safe singleton pattern using weak references.
SingletonMeta.__call__: Ensures only one instance of a class is created.
SingletonMeta.reset_instance: Resets the singleton instance for testing purposes.

ConfigLoader: Loads, validates, and manages configuration from a JSON file or a dictionary.
ConfigLoader.__init__: Initializes configuration from a file or dictionary.
ConfigLoader._validate_config: Validates that the configuration is a dictionary.
ConfigLoader.reload: Reloads configuration from a JSON file.
ConfigLoader.config: Returns a deep copy of the current configuration.

AppConfiguration: Thread-safe singleton class providing access to application configuration.
AppConfiguration.__init__: Initializes the application configuration using a file or dictionary.
AppConfiguration.reload: Reloads configuration if loaded from a file.
AppConfiguration.get: Retrieves a configuration value using a colon-separated path.
AppConfiguration.contains: Checks if a configuration key exists.
AppConfiguration.reset_instance: Resets the singleton instance.

# File: app_logging.py

LoggingService: Defines a protocol for a logging service that retrieves a logger instance.

LoggerConfig: Manages the configuration and setup of logger instances, ensuring proper logging levels and handlers.
LoggerConfig.\\init\\(): Initializes the logger with a specified name, level, and handlers.
LoggerConfig.\_configure_logger(): Creates and configures the logger instance with handlers.
LoggerConfig.\_add_unique_handler(): Ensures that the logger does not duplicate handlers.
LoggerConfig.\_default_stream_handler(): Returns a default StreamHandler with a formatted output.

SingletonLogger: Implements a thread-safe singleton pattern to provide a single logger instance across multiple threads.
SingletonLogger.get_logger(): Provides access to the single logger instance, ensuring only one is created.




--- END-OF-FILE

# Selection

Use the following rules for default seat selection:

1. Start from the furthest row from screen.
2. Start from the middle-most possible seat.
3. When a row is not enough to accommodate the number of tickets, it should overflow to the next row closer to screen.

User can choose seating position by specifying the starting position of the seats.
Seating assignment should follow this rule:
1. Starting from specified position, fill up all the empty seats in the same row all the way to the right of the cinema hall.
2. When there is not enough seats available, it should overflow to the next row closer to the screen.
3. Seat allocation for overflow follows the rules for default seat allocation.


