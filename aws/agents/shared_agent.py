"""Module containing some shared functionality use across MCP clients and servers"""
import json
import logging
import os
import threading
import time
from typing import Optional, List

from fastmcp import Client
from mcp.shared.exceptions import McpError

import pdb

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

class FileUtility(object):
    @staticmethod
    def normalize_path(directory_path, file_name = None):
        """
        Normalize file paths such that they always look like:
        C:/dir1/dir2/.../file
        """
        if file_name is None:
            target_path = directory_path
        else:
            target_path = os.path.join(directory_path, file_name)
        file_path = os.path.normpath(target_path)
        file_path.replace('\\', '/')
        return file_path

    @staticmethod
    def get_file_path_parts(file_path):
        """
        Note: A file_path like '.coverage' returns '.coverage' as file_name and '' as file_extension
        """
        split_ext = os.path.splitext(file_path)
        file_name = split_ext[0]
        file_extension = split_ext[1].lower()
        return (file_name, file_extension)



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

# FastMcpClient

class XxxFastMcpClient(object):
    def __init__(self, mcp_config: McpClientJsonConfiguration):
        self.mcp_servers_settings = mcp_config.get_mcp_servers_settings()
        self.llm_model = mcp_config.get_setting('client:preferred_llm')

        self.mcp_client = Client(self.mcp_servers_settings)
        runtime_dns_domain = os.environ.get('USERDNSDOMAIN')
        self._use_synaptic = runtime_dns_domain == 'AD.MLP.COM'
        self.logger = get_mcp_client_logger()

        self.resource_list = []
        self.tools = None
        self.message_history = []
        self.chat_client = None

    async def initialize_tools(self):
        self.tools = None
        async with self.mcp_client:
            tools = await self.mcp_client.list_tools()
            self.tools = [{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in tools] if self._use_synaptic else tools


    def _initialize_chat(self, chat_client):
        self.chat_client = chat_client
        self.message_history = []
        # If we want to define system prompt
        # self.message_history.append({
        #     "role": "system",
        #     "content": "You are a helpful assistant but you respond to all questions as if you were C3P0.",
        # })

    async def async_initialize(self):
        await self.initialize_tools()
        self._initialize_chat()

    #

    async def _is_connected(self, dump: bool = False):
        async with self.mcp_client:
            is_connected_result = self.mcp_client.is_connected()
            if dump: self.logger.debug("Client connected: %s", self.mcp_client.is_connected())
            return is_connected_result

    async def _ping(self, dump: bool = False):
        async with self.mcp_client:
            ping_result = await self.mcp_client.ping()
            if dump: self.logger.debug('ping_result: %s', ping_result)
            return ping_result

    # Resources

    async def _get_resources(self, dump: bool = False):
        try:
            async with self.mcp_client:
                resources = await self.mcp_client.list_resources() # resources -> list[mcp.types.Resource]
                self.resource_list.extend(resources)
                if dump:
                    self.logger.debug(f"Number of resources: {len(resources)}")
                    for resource in resources:
                        self.logger.debug('resource: %s', resource)
        except McpError as mcp_error:
            self.logger.warning('Unable to get resources; %s', mcp_error)

    async def _get_resource_templates(self, dump: bool = False):
        try:
            async with self.mcp_client:
                resource_templates = await self.mcp_client.list_resource_templates() # resource_templates -> list[mcp.types.ResourceTemplate]
                self.resource_list.extend(resource_templates)
                if dump:
                    self.logger.debug("Number of resource templates: %s", len(resource_templates))
                    for resource_template in resource_templates:
                        self.logger.debug('resource_template: %s', resource_template)
        except McpError as mcp_error:
            self.logger.warning('Unable to get resource templates; %s', mcp_error)

    async def _get_tools(self, dump: bool = False):
        try:
            async with self.mcp_client:
                tools = await self.mcp_client.list_tools() # tools -> list[mcp.types.Tool]
                self.resource_list.extend(tools)
                self.tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                } for tool in tools] if self._use_synaptic else tools

                if dump:
                    self.logger.debug(f"Number of tools: {len(tools)}")
                    for tool in tools:
                        self.logger.debug('tool: %s', tool)
        except McpError as mcp_error:
            self.logger.warning('Unable to get tools; %s', mcp_error)

    async def _get_prompts(self, dump: bool = False):
        try:
            async with self.mcp_client:
                prompts = await self.mcp_client.list_prompts()
                self.resource_list.extend(prompts)
                if dump:
                    self.logger.debug(f"Number of prompts: {len(prompts)}")
                    for prompt in prompts:
                        self.logger.debug('prompt: %s', prompt)
        except McpError as mcp_error:
            self.logger.warning('Unable to get prompts; %s', mcp_error)



    async def initialize_mcp_resource_list(
            self,
            dump_ping: bool=False,
            dump_connect: bool=False,
            dump_resources: bool=False,
            dump_resource_templates: bool = False,
            dump_tools: bool=False,
            dump_prompts: bool=False,
            dump_resource_list: bool = False):
        # async with self.mcp_client:
        await self._is_connected(dump_connect)
        await self._ping(dump_ping)
        self.resource_list = []
        await self._get_resources(dump_resources)
        await self._get_resource_templates(dump_resource_templates)
        await self._get_tools(dump_tools)
        await self._get_prompts(dump_prompts)
        if dump_resource_list:
            for resource in self.resource_list:
                print(resource)

    def initialize_chat(self, chat_client, system_prompt: Optional[str] = None):
        """
        # If we want to define system prompt
        # Example of system prompt:
        # "You are a helpful assistant but you respond to all questions as if you were C3P0.",
        """
        self.chat_client = chat_client
        self.message_history = []
        if system_prompt is not None:
            self.message_history.append({
                "role": "system",
                "content": system_prompt
            })

class BaseAgent(object):
    def __init__(self, mcp_config = McpClientJsonConfiguration):
        self.mcp_servers_settings = mcp_config.get_mcp_servers_settings()
        self._configure_logging(mcp_config.get_setting('logging'))

    def _configure_logging_file_handler(self, logging_setting: dict):
        enabled = logging_setting['enabled']
        logging_level = logging_setting['logging_level']
        logging_level = logging_level if logging_level in logging._nameToLevel else 'INFO'
        formatter = logging_setting['formatter']
        file_path = logging_setting['file_path']
        if enabled:
            logging_file_handler = logging.FileHandler(file_path)
            logging_file_handler.setLevel(logging._nameToLevel[logging_level])
            logging_file_handler.setFormatter(logging.Formatter(formatter))
            self.logger.addHandler(logging_file_handler)

    def _configure_logging_stream_handler(self, logging_setting: dict):
        enabled = logging_setting['enabled']
        logging_level = logging_setting['logging_level']
        logging_level = logging_level if logging_level in logging._nameToLevel else 'INFO'
        formatter = logging_setting['formatter']
        if enabled:
            logging_stream_handler = logging.StreamHandler()
            logging_stream_handler.setLevel(logging._nameToLevel[logging_level])
            logging_stream_handler.setFormatter(logging.Formatter(formatter))
            self.logger.addHandler(logging_stream_handler)

    def _configure_logging(self, logging_setting: dict):
        logger_name = logging_setting['logger']['name']
        logger_logging_level = logging_setting['logger']['logging_level'] # if logging_setting['logger']['logging_level'] in logging._nameToLevel else 'INFO'
        logger_logging_level = logger_logging_level if logger_logging_level in logging._nameToLevel else 'INFO'

        self.logger = logging.getLogger(logger_name)
        default_logger = logging.getLogger()
        print('len(self.logger.handlers):', len(self.logger.handlers))
        print('len(self.logger.handlers):', len(default_logger.handlers))

        # for handler in list(self.logger.handlers):  # Create a list to iterate over
        #     self.logger.removeHandler(handler)
        #     handler.close()  # It's good practice to close handlers if they manage resources

        self.logger.setLevel(logging._nameToLevel[logger_logging_level])

        self._configure_logging_file_handler(logging_setting['fileHandler'])
        self._configure_logging_stream_handler(logging_setting['streamHandler'])


class BaseMcpAgent(BaseAgent):
    def __init__(self, mcp_config = McpClientJsonConfiguration):
        super().__init__(mcp_config)
        self.mcp_client = Client(self.mcp_servers_settings)
        # MCP resource
        self.resource_list = []
        self.resource_template_list = []
        self.tool_list = []
        self.prompt_list = []
        self.mcp_resource_getters = {
            'resources': self._get_resources,
            'resource_templates': self._get_resource_templates,
            'tools': self._get_tools,
            'prompts': self._get_prompts
        }

    async def initialize(self, resource_type_list: Optional[List[str]]):
        await self._get_mcp_resources(resource_type_list)

    async def _get_mcp_resources(self, resource_type_list: Optional[List[str]]):
        if resource_type_list is None:
            resource_type_list = ['resources', 'resource_templates', 'tools', 'prompts']

        for resource_type in resource_type_list:
            mcp_resource_getter_function = self.mcp_resource_getters.get(resource_type)
            if mcp_resource_getter_function:
                self.logger.debug(f"Loading resource type: {resource_type}")
                await mcp_resource_getter_function()
            else:
                self.logger.warning(f"Unknown resource type '{resource_type}' encountered. Skipping.")

    async def _get_resources(self):
        try:
            async with self.mcp_client:
                resources = await self.mcp_client.list_resources()  # resources -> list[mcp.types.Resource]
                self.resource_list = resources
        except McpError as mcp_error:
            self.logger.warning('Unable to get resources; %s', mcp_error)

    async def _get_resource_templates(self):
        try:
            async with self.mcp_client:
                resource_templates = await self.mcp_client.list_resource_templates() # resource_templates -> list[mcp.types.ResourceTemplate]
                self.resource_template_list = resource_templates
        except McpError as mcp_error:
            self.logger.warning('Unable to get resource templates; %s', mcp_error)

    async def _get_tools(self):
        try:
            async with self.mcp_client:
                tools = await self.mcp_client.list_tools() # tools -> list[mcp.types.Tool]
                self.tool_list = tools
        except McpError as mcp_error:
            self.logger.warning('Unable to get tools; %s', mcp_error)

    async def _get_prompts(self):
        try:
            async with self.mcp_client:
                prompts = await self.mcp_client.list_prompts()
                self.prompt_list = prompts
        except McpError as mcp_error:
            self.logger.warning('Unable to get prompts; %s', mcp_error)

