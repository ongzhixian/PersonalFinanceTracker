"""Module containing some shared functionality use across MCP clients and servers"""
import json
import logging
import os

def get_mcp_client_logger(logger_name: str = None):
    default_format = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    message_centric_format = "[%(levelname).3s] %(message)s"
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
    return logging.getLogger(logger_name)


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
