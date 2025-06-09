import asyncio
import json
from typing import Optional, List

from fastmcp import Client
import mcp
from mcp.shared.exceptions import McpError

from google import genai
from google.genai import types
from google.genai.types import Content, Part, GenerateContentResponse

from shared_agent import McpClientJsonConfiguration, BaseMcpAgent

import pdb

########################################



class BasicGeminiAgent(BaseMcpAgent):
    """Represents a standalone agent"""

    def __init__(self, mcp_config = McpClientJsonConfiguration):
        super().__init__(mcp_config)
        self.gemini_ai_api_key = mcp_config.get_secret('gemini-ai-api-secret-key')
        self.large_language_model = mcp_config.get_setting('gemini:preferred_model')
        self.chat_client = genai.Client(api_key=self.gemini_ai_api_key)
        self.message_history: List[Content] = []
        self.chat_completion_configuration = None

    async def initialize(self, resource_type_list: Optional[List[str]] = None):
        await super().initialize(resource_type_list)

        system_prompt = "You are a world-class software engineer."
        # system_prompt = "You are a cat. Your name is Neko."
        self.chat_completion_configuration = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1
        )
        self.logger.debug('Agent initialized.')

    #

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

    async def process_chat_request(self, query: str) -> str:

        # self.message_history.append({
        #     "role": "user",
        #     "content": query
        # })
        self.message_history.append(
            Content(
                role='user',
                parts=[Part(text=query)]
            )
        )

        # Reference: https://ai.google.dev/api/caching#Content
        # Role = 'user' or 'model'.

        response = self.chat_client.models.generate_content(
            model=self.large_language_model,
            config=self.chat_completion_configuration,
            contents=self.message_history) # response is google.genai.types.GenerateContentResponse

        # Gemini returns a list of

        print('RESPONSE:', response)
        pdb.set_trace()


        print('RESPONSE TEXT:', response.text)



        return

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

    async def start_interactive_chat(self):
        """Runs an interactive chat loop"""
        print("Type your queries or 'quit' to exit.\n")
        query = 'hello'
        response = await self.process_chat_request(query)
        # print(f"{response['role']:>9}: {response['content']}".strip())
        print('END-OF-CHAT')

        # while True:
        #     try:
        #         query = input(f"[{len(self.message_history):03}]{'USER':>4}: ").strip()
        #         if query.lower() == 'quit':
        #             break
        #
        #         response = await self.get_chat_response(query)
        #         if response is None:
        #             continue
        #         print(f"{response['role']:>9}: {response['content']}".strip())
        #         print()
        #
        #     except Exception as e:
        #         print(f"Error: {str(e)}")



async def main():
    mcp_config = McpClientJsonConfiguration('./gemini_agent_config.json')
    fast_mcp_client = BasicGeminiAgent(mcp_config)
    await fast_mcp_client.initialize()
    await fast_mcp_client.start_interactive_chat()

    # print("\n--- Test Case 1: resource_type_list is None ---")
    # await fast_mcp_client.initialize(resource_type_list=None)
    #
    # print("\n--- Test Case 2: resource_type_list is not provided ---")
    # await fast_mcp_client.initialize()  # resource_type_list will be None by default
    #
    # print("\n--- Test Case 3: resource_type_list is an empty list ---")
    # await fast_mcp_client.initialize(resource_type_list=[])
    #
    # print("\n--- Test Case 4: resource_type_list is a non-empty list ---")
    # await fast_mcp_client.initialize(resource_type_list=['my_custom_resource'])
    #
    # print("\n--- Test Case 5: resource_type_list is a different non-empty list ---")
    # await fast_mcp_client.initialize(resource_type_list=['images', 'videos'])

    # await fast_mcp_client.async_initialize()
    # # await fast_mcp_client.async_debug_dump()
    # await fast_mcp_client.start_chat()


# async def main():
#     mcp_config = McpClientJsonConfiguration('./programmer_agent_config.json')
#     fast_mcp_client = ConduitFastMcpClient(mcp_config)
#     await fast_mcp_client.initialize_mcp_resource_list(dump_resource_list=False)
#     # Add customizations
#     chat_client = fast_mcp_client._get_chat_client()
#     system_prompt = fast_mcp_client._get_system_prompt()
#     system_prompt = 'You are a world-class software engineer.'
#     fast_mcp_client.initialize_chat(chat_client, system_prompt)
#     await fast_mcp_client.start_chat()
#

if __name__ == "__main__":
    asyncio.run(main())
