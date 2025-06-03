"""
"""
import logging
import asyncio
import json
from os import environ
from contextlib import AsyncExitStack
from fastmcp import Client, FastMCP
from conduit_client import OpenAI

import pdb

runtime_dns_domain = environ.get('USERDNSDOMAIN')
use_synaptic = runtime_dns_domain == 'AD.MLP.COM'

CLIENT_NAME = 'CLIENT XYZ'
PREFERRED_LLM = 'gemini-1.5-flash-002'



class FastMcpClient():
    def __init__(self):

        # Example transports (more details in Transports page)
        # server_instance = FastMCP(name="TestServer")  # In-memory server
        # http_url = "https://example.com/mcp"  # HTTP server URL
        # server_script = "my_mcp_server.py"  # Path to a Python server file
        #
        # # Client automatically infers the transport type
        # client_in_memory = Client(server_instance)
        # client_http = Client(http_url)
        #
        # client_stdio = Client(server_script)
        #
        # print(client_in_memory.transport)
        # print(client_http.transport)
        # print(client_stdio.transport)

        # Expected Output (types may vary slightly based on environment):
        # <FastMCP(server='TestServer')>
        # <StreamableHttp(url='https://example.com/mcp')>
        # <PythonStdioTransport(command='python', args=['/path/to/your/my_mcp_server.py'])>

        self.mcp_client_config = {
            "mcpServers": {
                "demo_mcp_server": {
                    "url": "http://127.0.0.1:4500/mcp",
                    "transport": "streamable-http"
                }
                # A local server running via stdio
                # "assistant": {
                #     "command": "C:/Code/zong/pft/aws/.venv/Scripts/python.exe",
                #     "args": ["C:/Code/zong/pft/aws/agents/demo_mcp_server.py"],
                #     "env": {"DEBUG": "true"}
                # }
            }
        }
        self.mcp_client = Client(self.mcp_client_config)

    def _get_chat_client(self, preferred_llm:str='gemini-1.5-flash-002'):
        if use_synaptic:  # Use conduit
            client = OpenAI()
            client.model = preferred_llm
            return client
        else:
            # Use other AI providers
            # from anthropic import Anthropic
            # client = Anthropic()
            # return client
            return None

    def _initialize_chat(self):
        self.message_history = []
        # If we want to define system prompt
        # self.message_history.append({
        #     "role": "system",
        #     "content": "You are a helpful assistant but you respond to all questions as if you were C3P0.",
        # })

    async def _initialize_tools(self):
        self.tools = None
        async with self.mcp_client:
            tools = await self.mcp_client.list_tools()
            self.tools = [{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in tools] if use_synaptic else tools
            logger.debug(f"Available tools: %s", tools)
            response = await self.mcp_client.list_resources()
            print(f">> Available resources: {response}")

    async def initialize(self):
        # Initialize session and client objects
        # self.session: Optional[ClientSession] = None
        # self.exit_stack = AsyncExitStack()
        self.chat_client = self._get_chat_client()
        self._initialize_chat()
        await self._initialize_tools()


    async def chat_loop(self):
        """Runs an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.\n")
        #await self.initialize()

        while True:
            try:
                query = input(f"[{len(self.message_history):03}]{'USER':>4}: ").strip()
                if query.lower() == 'quit':
                    break

                response = await self.get_chat_response(query)
                if response is None:
                    continue
                print(f"{response['role']:>9}: {response['content']}".strip())
                print()

            except Exception as e:
                print(f"Error: {str(e)}")

    async def get_chat_response(self, query: str) -> str:
        self.message_history.append({
            "role": "user",
            "content": query
        })

        if use_synaptic:
            response = self.chat_client.chat.completions.create(
                model=self.chat_client.model,
                messages=self.message_history,
                tools=self.tools
            )
            return await self.handle_response(response)

        return 'Unhandled. No non-synaptic chat client defined'

    async def handle_response(self, response):
        # response = ChatCompletion object
        logging.debug('Chat response: %s', response)

        response_choice_count = len(response.choices)
        logging.debug('Number of response choice(s): %s', len(response.choices))

        # Maybe this should be more generic; there shouldn't be any differences between handling single vs multiple
        if response_choice_count == 1:
            choice = response.choices[0]
            logging.debug('Response choice finish reason: %s', choice.finish_reason)

            if choice.finish_reason == 'stop' and choice.message.__class__.__name__ == 'ChatCompletionMessage':
                chat_entry = { "role": choice.message.role, "content": choice.message.content }
                self.message_history.append(chat_entry)
                return chat_entry

            if choice.finish_reason == 'tool_calls' and choice.message.__class__.__name__ == 'ChatCompletionMessage':
                tool_calls = choice.message.tool_calls
                for tool in tool_calls:
                    tool_func = tool.function
                    async with self.mcp_client:
                        tool_call_result_list = await self.mcp_client.call_tool(tool_func.name, json.loads(tool_func.arguments))
                        logging.debug('Tool call result: %s', tool_call_result_list)
                        if len(tool_call_result_list) == 1:
                            result = tool_call_result_list[0] #
                            if result.__class__.__name__ == 'TextContent' and result.type == 'text':
                                self.message_history.append({
                                    "role": choice.message.role,
                                    "tool_name": tool_func.name,
                                    "parameters": json.loads(tool_func.arguments),
                                    "result": result.text
                                })
                                chat_entry = {"role": choice.message.role, "content": result.text}
                                self.message_history.append(chat_entry)
                                return chat_entry


            logging.warning('Unhandled multiple choice scenario. Number of response choice: %s', response_choice_count)
            return None
        else:
            logging.warning('Unhandled multiple choice scenario. Number of response choice: %s', response_choice_count)
            return None

    def __process_query(query):
        return f'TODO -- {query}'



# self.ai_client = self.get_ai_client()
# self.ai_model = 'gemini-1.5-flash-002'
# self.message_history = []

# async def cleanup(self):
#     """Clean up resources"""
#     await AsyncExitStack().aclose()


########################################

class McpConfig(object):
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

    def get_mcp_servers_settings(self):
        mcp_servers_settings = self._get_configuration('mcpServers', return_top_level_dict=True)
        return mcp_servers_settings


def __configure_logging():
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
    return logging.getLogger()

logger = __configure_logging()


async def main():
    mcp_config = McpConfig('./conduit_mcp_client.json')
    mcp_servers_settings = mcp_config.get_mcp_servers_settings()
    # mcp_config.get_mcp_transport_settings()
    # mcp_client_config = {
    #     "mcpServers": {
    #         "demo_mcp_server": {
    #             "url": "http://127.0.0.1:4500/mcp",
    #             "transport": "streamable-http"
    #         }
    #         # A local server running via stdio
    #         # "assistant": {
    #         #     "command": "C:/Code/zong/pft/aws/.venv/Scripts/python.exe",
    #         #     "args": ["C:/Code/zong/pft/aws/agents/demo_mcp_server.py"],
    #         #     "env": {"DEBUG": "true"}
    #         # }
    #     }
    # }
    client = Client(mcp_servers_settings)
    # Connection is established here
    async with client:
        print(f"Client connected: {client.is_connected()}")

        # Make MCP calls within the context
        # tools = await client.list_tools()
        # print(f"Available tools: {tools}")
        #
        # if any(tool.name == "greet" for tool in tools):
        #     result = await client.call_tool("greet", {"name": "World"})
        #     print(f"Greet result: {result}")

    # Connection is closed automatically here
    print(f"Client connected: {client.is_connected()}")


if __name__ == "__main__":
    logger.info('Start')
    asyncio.run(main())



