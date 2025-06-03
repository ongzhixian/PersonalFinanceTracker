import asyncio
import json
import logging
from os import environ

from fastmcp import Client
import mcp

from shared_mcp import get_mcp_client_logger, McpClientJsonConfiguration


import pdb

logger = get_mcp_client_logger()

runtime_dns_domain = environ.get('USERDNSDOMAIN')
use_synaptic = runtime_dns_domain == 'AD.MLP.COM'

PREFERRED_LLM = 'gemini-1.5-flash-002'

########################################

class FastMcpClient():

    def __init__(self, mcp_config = McpClientJsonConfiguration):
        self.mcp_servers_settings = mcp_config.get_mcp_servers_settings()
        runtime_dns_domain = environ.get('USERDNSDOMAIN')
        self._use_synaptic = runtime_dns_domain == 'AD.MLP.COM'
        self.gemini_ai_api_key = mcp_config.get_secret("gemini-ai-api-secret-key")
        self.client_model = mcp_config.get_setting('gemini:preferred_model')
        # self.client_model = 'gemini-2.0-flash'
        # gemini_model = self.app_configuration.get('secrets:gemini-model')
        # self.client_model = gemini_model

    def _get_chat_client(self, preferred_llm:str='gemini-1.5-flash-002'):
        # Use other AI providers
        # from anthropic import Anthropic
        # client = Anthropic()
        # return client
        from google import genai
        return genai.Client(api_key=self.gemini_ai_api_key)



    def _initialize_chat(self):
        self.message_history = []
        # If we want to define system prompt
        # self.message_history.append({
        #     "role": "system",
        #     "content": "You are a helpful assistant but you respond to all questions as if you were C3P0.",
        # })
        self.chat_client = self._get_chat_client()

    async def _initialize_tools(self):
        self.tools = None
        async with self.mcp_client:
            tools = await self.mcp_client.list_tools()
            self.tools = [{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in tools] if use_synaptic else tools
            self.logger.debug(f"Available tools: %s", tools)
            response = await self.mcp_client.list_resources()
            print(f">> Available resources: {response}")


    async def async_debug_dump(self):
        async with (Client(self.mcp_servers_settings) as client):
            print(f"Client connected: {client.is_connected()}")
            # At minimal, we should do a ping. If we don't do anything and just exit client context,
            # it throws the server off.
            ping_result = await client.ping()
            print('ping_result', ping_result)

            resources = await client.list_resources()
            # resources -> list[mcp.types.Resource]
            logger.debug(f"Number of resources: {len(resources)}")
            for resource in resources:
                print('resource', resource)

            resource_templates = await client.list_resource_templates()
            # resource_templates -> list[mcp.types.ResourceTemplate]
            print(f"Number of resource templates: {len(resource_templates)}")
            print('resource_templates', resource_templates)
            for resource_template in resource_templates:
                print('resource_template', resource_template)


            # readme_content = await client.read_resource("file:///path/to/README.md")
            # # readme_content -> list[mcp.types.TextResourceContents | mcp.types.BlobResourceContents]
            # print(readme_content[0].text)  # Assuming text

            import pdb

            # Read a resource generated from a template
            # user_profile_list = await client.read_resource("conduit-mcp://user-profile/london")
            # if len(user_profile_list) > 0:
            #     print(user_profile_list[0].text)  # Assuming text JSON
            #
            # response_list = await client.read_resource("conduit-mcp://models")
            # # response_list -> list[mcp.types.TextResourceContents | mcp.types.BlobResourceContents]
            # print('response_list', response_list)
            # for response in response_list:
            #     response_type = type(response).__name__
            #     match response_type:
            #         case 'TextResourceContents':
            #             match response.mimeType:
            #                 case 'application/json':
            #                     print(f'TODO: {response_type}, mimeType: {response.mimeType}')
            #                     data = json.loads(response.text)
            #                     return data
            #                 case _:
            #                     print('Unhandled MIME type')
            #         case _:
            #             print(f'Unhandled response type: {response_type}')

            # if len(model_list) > 0:
            #     print(user_profile_list[0].text)  # Assuming text JSON

            # result = await client.call_tool("add", {"a": 1, "b": 2})
            # print(result)
        print(f"Client connected: {client.is_connected()}")

    async def async_initialize(self):
        # Initialize session and client objects
        # self.session: Optional[ClientSession] = None
        # self.exit_stack = AsyncExitStack()
        self._initialize_chat()
        # await self._initialize_tools()

    async def get_chat_response(self, query: str) -> str:
        self.message_history.append({
            "role": "user",
            "content": query
        })

        if self._use_synaptic:
            response = await self.session.list_tools()
            print('\nlist_tools response: ', response)
            available_functions = [{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in response.tools]

            response = self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=self.message_history,
                functions=available_functions,
                function_call="auto"
            )
            print('\nFULL RESPONSE: ', response)
            response_message = response.choices[0].message
            if response_message.function_call is not None:
                print('==> MAKE FUNCTION CALL')
                function_def = response_message.function_call
                tool_response = await self.session.call_tool(name=function_def.name,
                                                             arguments=json.loads(function_def.arguments))
                if tool_response.content[0].type == 'text':
                    self.message_history.append({
                        "type": "tool_result",
                        "tool_use_id": response.id,
                        "content": tool_response.content[0].text
                    })
                    print(tool_response.content[0].text)
                    print('Message count: ', len(self.message_history))
                else:
                    print('TOOL_RESPONSE: ', tool_response)

            else:
                self.message_history.append({
                    "role": response_message.role,
                    "content": response_message.content
                })
                print(f'{response_message.role.upper()}: {response_message.content}')
                # print('\nFULL RESPONSE: ', response)
                # return response
                return response_message.content
        else:
            pass
            # Initial Claude API call
            # response = self.anthropic.messages.create(
            #     model="claude-3-5-sonnet-20241022",
            #     max_tokens=1000,
            #     messages=messages,
            #     tools=available_tools
            # )
        return ''

    async def start_chat(self):
        """Runs an interactive chat loop"""
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



async def main():
    mcp_config = McpClientJsonConfiguration('./gemini_mcp_client.json')

    fast_mcp_client = FastMcpClient(mcp_config)
    await fast_mcp_client.async_initialize()
    # await fast_mcp_client.async_debug_dump()
    await fast_mcp_client.start_chat()



if __name__ == "__main__":
    asyncio.run(main())