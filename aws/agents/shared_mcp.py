"""Module containing some shared functionality use across MCP clients and servers"""
import json
import logging
import os
import threading
import time

def get_mcp_client_logger(logger_name: str = None):
    default_format = "\n[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    message_centric_format = "[%(levelname).3s] %(message)s"
    # default_format = message_centric_format
    logging.basicConfig(
        level=logging.DEBUG,
        format=default_format,
        datefmt="%d/%b/%Y %H:%M:%S")
    # Suppress logging messages from 3rd party modules that we do not care about
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('mcp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    logging.getLogger('sse_starlette').setLevel(logging.INFO)
    logging.getLogger('conduit_client').setLevel(logging.INFO)
    logging.getLogger('openai._base_client.request').setLevel(logging.INFO)
    return logging.getLogger(logger_name)

# Content



# Configuration

class JsonConfiguration(object):
    def __init__(self, configuration_json_file_path:str):
        with open(configuration_json_file_path) as input_file:
            self.json_configuration = json.load(input_file)

    def _get_configuration(
        self,
        colon_delimited_key: str,
        default=None,
        raise_on_missing=False,
        return_top_level_dict:bool=False
    ):
        """
        Retrieve value from nested dict using colon-delimited key.
        If a key is missing, return `default` or raise KeyError if raise_on_missing is True.
        If return_top_level_dict is True and the key is top-level, return {key: value}.
        """
        keys = colon_delimited_key.split(':')
        value = self.json_configuration

        # Special handling for top-level key if requested
        if return_top_level_dict and len(keys) == 1 and keys[0] in value:
            return {keys[0]: value[keys[0]]}

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                if raise_on_missing:
                    raise KeyError(f"Key path '{colon_delimited_key}' not found at '{key}'")
                return default
        return value

class McpClientJsonConfiguration(JsonConfiguration):
    def __init__(self, configuration_json_file_path: str):
        super().__init__(configuration_json_file_path)

    def get_mcp_servers_settings(self):
        mcp_servers_settings = self._get_configuration('mcpServers', return_top_level_dict=True)
        return mcp_servers_settings

    def get_secret(self, key: str):
        secrets = self._get_configuration('secrets')
        #
        secrets_file_path_setting = secrets['file-path'] if 'file-path' in secrets else None
        if secrets_file_path_setting is None:
            raise Exception('File path not defined.')
        secrets_file_path = os.path.normpath(os.path.expandvars(secrets_file_path_setting))

        secret_key = secrets[key]
        with open(secrets_file_path, "r", encoding="utf-8") as f:
            secrets = json.load(f)
            return secrets[secret_key] if secret_key in secrets else None

    def get_setting(self, key: str):
        return self._get_configuration(key)

class McpServerJsonConfiguration(JsonConfiguration):
    def __init__(self, configuration_json_file_path: str):
        super().__init__(configuration_json_file_path)

    def get_mcp_transport_settings(self) -> dict:
        """
        1. mcp.run(transport="stdio") # Same mcp.run()
        2. mcp.run(transport="sse", host="127.0.0.1", port=4500)
        3. mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)
        """
        transport_type = self._get_configuration('mcp:transport_type').lower()
        if transport_type == 'stdio':
            return {
                "transport" : "stdio"
            }
        else:
            transport_settings = self._get_configuration(f'mcp:{transport_type}')
            return {
                "transport": transport_type,
                "host": transport_settings['host'],
                "port": transport_settings['port'],
                "path": transport_settings['path'] if 'path' in transport_settings else '/mcp-server/mcp'
            }

    def get_uvicorn_settings(self):
        uvicorn_settings = self._get_configuration('uvicorn')
        return uvicorn_settings

    def get_fastapi_settings(self):
        fastapi_settings = self._get_configuration('fastapi')
        return fastapi_settings

# Idle timeout handler

class IdleTimeoutManager:
    """
    Manages idle timeout for the server.
    If no request is received for `timeout_seconds`, the process will terminate.
    Optionally, a callback can be provided to save state before exit.
    """
    def __init__(self, timeout_seconds: int = 300, on_timeout=None):
        self.timeout_seconds = timeout_seconds
        self._last_request_time = time.time()
        self._lock = threading.Lock()
        self._watcher_thread = None
        self._started = False
        self._on_timeout = on_timeout

    def update(self) -> None:
        """Update the timestamp of the last handled request."""
        with self._lock:
            self._last_request_time = time.time()

    def _watcher(self) -> None:
        """Background thread to terminate the process if idle for too long."""
        while True:
            time.sleep(10)
            with self._lock:
                idle_time = time.time() - self._last_request_time
            if idle_time > self.timeout_seconds:
                print(f"[IDLE TIMEOUT] No requests for {idle_time:.0f}s, saving state and shutting down.")
                if self._on_timeout:
                    try:
                        self._on_timeout()
                    except Exception as e:
                        print(f"[IDLE TIMEOUT] Exception during save_state: {e}")
                os._exit(0)  # Immediate exit

    def start(self) -> None:
        """Start the idle timeout watcher thread (only once)."""
        if not self._started:
            self._watcher_thread = threading.Thread(target=self._watcher, daemon=True)
            self._watcher_thread.start()
            self._started = True
