import sys
import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack
from os import environ

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# functions = [
#     {
#         "name": "get_current_weather",
#         "description": "Get the current weather in a given location",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "location": {
#                     "type": "string",
#                     "description": "The city and state, e.g. San Francisco, CA",
#                 },
#                 "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#             },
#             "required": ["location"],
#         },
#     },
#     {
#         "name": "echo_message",
#         "description": "echo any arbitrary string",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "message": {
#                     "type": "string",
#                     "description": "string to echo"
#                 }
#             },
#             "required": ['message'],
#         },
#     },
#     {
#         "name": "end_conversation",
#         "description": "Function to call to end a conversation"
#     }
# ]

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.ai_client = self.get_ai_client()
        self.ai_model = 'gemini-1.5-flash-002'
        self.message_history = []
        # If we want to define system prompt
        # self.message_history.append({
        #     "role": "system",
        #     "content": "You are a helpful assistant but you respond to all questions as if you were C3P0.",
        # })

    
    def __use_synaptic(self) -> bool:
        runtime_dns_domain = environ.get('USERDNSDOMAIN')
        return runtime_dns_domain == 'AD.MLP.COM'
    
    def get_ai_client(self):
        if self.__use_synaptic(): # Use conduit
            from conduit_client import OpenAI
            client = OpenAI()
            return client
        else:
            #Use other AI providers
            # from anthropic import Anthropic
            # client = Anthropic()
            # return client
            return None
        
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        
        print('server_script_path', server_script_path)

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        print('Connecting to server')

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        #print('\nlist_tools response: ', response)
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                print('Message history count: ', len(self.message_history))
                query = input("\n    Query: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.__process_query(query)
                #print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def get_chat_response(self, query: str) -> str:
        
        self.message_history.append({
            "role": "user",
            "content": query
        })

        if self.__use_synaptic():
            response = await self.session.list_tools()
            print('\nlist_tools response: ', response)
            available_functions = [{
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            } for tool in response.tools ]

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
                tool_response = await self.session.call_tool(name=function_def.name, arguments=json.loads(function_def.arguments))
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
                #return response
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

            

    async def __process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""

        response = await self.get_chat_response(query)
        return response
        

        #print('\nCHAT RESPONSE:', response)
        #
        # Process response and handle tool calls
        # final_text = []

        # assistant_message_content = []
        # for content in response.content:
        #     if content.type == 'text':
        #         final_text.append(content.text)
        #         assistant_message_content.append(content)
        #     elif content.type == 'tool_use':
        #         tool_name = content.name
        #         tool_args = content.input

        #         # Execute tool call
        #         result = await self.session.call_tool(tool_name, tool_args)
        #         final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

        #         assistant_message_content.append(content)
        #         messages.append({
        #             "role": "assistant",
        #             "content": assistant_message_content
        #         })
        #         messages.append({
        #             "role": "user",
        #             "content": [
        #                 {
        #                     "type": "tool_result",
        #                     "tool_use_id": content.id,
        #                     "content": result.content
        #                 }
        #             ]
        #         })

        #         # Get next response from Claude
        #         response = self.anthropic.messages.create(
        #             model="claude-3-5-sonnet-20241022",
        #             max_tokens=1000,
        #             messages=messages,
        #             tools=available_tools
        #         )

        #         final_text.append(response.content[0].text)

        # return "\n".join(final_text)




async def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_chat_client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
