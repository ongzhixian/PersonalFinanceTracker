"""Shared Application Utilities (and functions)
Functions:
    get_script_name
Classes:
    LoggerFactory (static)
"""
import json
import logging
import os

# FUNCTIONS

def get_script_name(__file__:str):
    return f"{os.path.basename(__file__).replace('.py', '')}"


# CLASSES

class LoggerFactory:
    def __init__(self):
        pass

    def __get_standard_log_file_name(name):
        return f"{name}.log"

    def get_logger(name, level=logging.INFO):
        log_file_name = LoggerFactory.__get_standard_log_file_name(name)
        logger = logging.getLogger(name)
        logger.setLevel(level)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Create file handler
        fh = logging.FileHandler(log_file_name)
        fh.setFormatter(formatter)

        # Create console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(fh)
            logger.addHandler(ch)

        logger.debug('%s logger initialized.', name)
        return logger


class AppConfiguration:
    """Handles loading and saving sync configuration."""

    def __init__(self, main_script_name, configuration_file_name=None):
        self.logger = LoggerFactory.get_logger(main_script_name)

        if configuration_file_name is None:
            configuration_file_name = f"{main_script_name}-config.json"

        self.configuration_file_name = configuration_file_name
        self.logger.debug(f"Configuration file name '{self.configuration_file_name}'.")

        self.config = self.load_config()
        self.logger.debug(f"Configuration loaded.")

    def load_config(self):
        try:
            with open(self.configuration_file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Configuration file '{self.configuration_file_name}' not found.")
            return {}

    def save_config(self):
        with open(self.configuration_file_name, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)
        self.logger.info(f"Sync config saved to '{self.configuration_file_name}'.")

    def get(self, key_path, default=None):
        keys = key_path.split(':')
        current_data = self.config

        for key in keys:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            else:
                return default
        return current_data

    def update(self, key_path, value):
        keys = key_path.split(':')
        current_data = self.config

        for i, key in enumerate(keys):
            # if is last key in the path (leaf) and current_data is dict
            if i == len(keys) - 1 and isinstance(current_data, dict):
                self.logger.info(f'Configuration {key_path} saved.')
                current_data[key] = value
                self.save_config()
                return
            else:
                if isinstance(current_data, dict):
                    # Create nested dictionary if it doesn't exist or is not a dict
                    if key not in current_data:
                        current_data[key] = {}
                    # Traverse
                    if isinstance(current_data[key], dict):
                        current_data = current_data[key]

        # Configuration not saved; most likely key_path is not dict
        self.logger.warning(f'Configuration {key_path} not saved.')


class SecretsManager:
    """Manages retrieval of secrets from the user secrets file."""

    def __init__(self, main_script_name:str, secrets_file_path:str):
        self.logger = LoggerFactory.get_logger(main_script_name)

        self.secrets_file_path = os.path.normpath(os.path.expandvars(secrets_file_path))
        self.logger.debug("Secrets file path %s.", self.secrets_file_path)

    def get_secrets(self) -> dict:
        try:
            with open(self.secrets_file_path, "r", encoding="utf-8") as f:
                secrets = json.load(f)
                self.logger.debug("Secrets loaded.")
                return secrets
        except Exception as ex:
            self.logger.error("Error reading secrets file at %s: %s",self.secrets_file_path, ex)
            raise
