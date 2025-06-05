import asyncio
import json
import logging
import time
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

    def __init__(self, mcp_config: McpClientJsonConfiguration):
        self.mcp_servers_settings = mcp_config.get_mcp_servers_settings()
        self.llm_model = mcp_config.get_setting('client:preferred_llm')
        self.mcp_client = Client(self.mcp_servers_settings)

        runtime_dns_domain = environ.get('USERDNSDOMAIN')
        self._use_synaptic = runtime_dns_domain == 'AD.MLP.COM'

    def _get_chat_client(self, preferred_llm:str='gemini-1.5-flash-002'):
        if use_synaptic:  # Use Conduit
            from conduit_client import AsyncOpenAI
            client = AsyncOpenAI()
            client.model = preferred_llm
            return client
        else:
            # Use other AI providers
            # from anthropic import Anthropic
            # client = Anthropic()
            # return client
            raise ValueError('NOT CHAT CLIENT')
            return None

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
            # logger.debug(f"Available tools: %s", tools)
            # response = await self.mcp_client.list_resources()
            # print(f">> Available resources: {response}")

    def _handle_read_resource_responses(self, read_resource_responses):
        # print('read_resource_responses', read_resource_responses)
        resource_list = []
        for read_resource_response in read_resource_responses:
            read_resource_response_class_name = read_resource_response.__class__.__name__.lower()
            match read_resource_response_class_name:
                case 'textresourcecontents':
                    if read_resource_response.mimeType == 'application/json':
                        resource = json.loads(read_resource_response.text)
                        resource_class_name = resource.__class__.__name__.lower()
                        match resource_class_name:
                            case 'dict':
                                resource_list.append(resource)
                            case 'list':
                                resource_list.extend(resource)
                            case _:
                                logger.warning('Unhandled resource_class_name %s', resource_class_name)
                    if read_resource_response.mimeType == 'text/plain':
                        return read_resource_response.text
                case _:
                    logger.warning('Unhandled read_resource_response_class_name %s', read_resource_response_class_name)
        return resource_list

    def _initialize_chat_prompt(self, resource_list):
        """
        Attempt to work around MCP limitations by giving ability to read resources.
        This currently goes against the way MCP wants to work...so KIV and go tool_call oriented.
        """
        mcp_resources = "\n".join([ str(resource) for resource in resource_list ])
        add_instructions = """
        If the query requires reading MCP resources and making tool calls from given MCP resources:
        1. If resource is not in given MCP resources list, prefix the the name with 'TO-IMPLEMENT'.
        2. Respond as:
        ```
        {
          tasks: [
            {
              "action": "read_resource",
              "explain": <text description explaining why this action is necessary>,
              "resource": <MCP RESOURCE URI>
            },
            {
                "action": "tool_call",
                "explain": <text description explaining why this action is necessary>,
                "name": <TOOL_NAME>,
                "description": <TOOL_DESCRIPTION>,
                "parameters": <TOOL_INPUT_SCHEMA>
            }
            ...
          ]
        }
        ```
        """
        # You are a world-class software engineer.
        seed_prompt = f"You are a world-class software engineer.\n\nGiven following MCP resources:\n\n```\n{mcp_resources}\n```\n\n{add_instructions}"
        # print('seed_prompt:', seed_prompt)
        # self.message_history.append(f"Given following MCP resources:\n\n```\n{mcp_resources}\n```")
        self.message_history.append({
            "role": "system",
            "content": seed_prompt
        })

    async def async_debug_dump(
            self,
            dump_resources: bool=False,
            dump_resource_templates: bool=False,
            dump_tools: bool=False,
            dump_prompts: bool=False,
            dump_ping: bool=False,
            dump_connect: bool=False):
        async with self.mcp_client:
            self.resource_list = []

            if dump_connect:
                logger.debug("Client connected: %s", self.mcp_client.is_connected())

            ping_result = await self.mcp_client.ping()
            if dump_ping:
                logger.debug('ping_result: %s', ping_result)

            resources = await self.mcp_client.list_resources()
            # resources -> list[mcp.types.Resource]
            self.resource_list.extend(resources)
            if dump_resources:
                logger.debug(f"Number of resources: {len(resources)}")
                for resource in resources:
                    logger.debug('resource: %s', resource)

            resource_templates = await self.mcp_client.list_resource_templates()
            # resource_templates -> list[mcp.types.ResourceTemplate]
            self.resource_list.extend(resource_templates)
            if dump_resource_templates:
                logger.debug("Number of resource templates: %s", len(resource_templates))
                for resource_template in resource_templates:
                    logger.debug('resource_template: %s', resource_template)

            tools = await self.mcp_client.list_tools()
            # tools -> list[mcp.types.Tool]
            self.resource_list.extend(tools)
            if dump_tools:
                logger.debug(f"Number of tools: {len(tools)}")
                for tool in tools:
                    logger.debug('tool: %s', tool)

            prompts = await self.mcp_client.list_prompts()
            self.resource_list.extend(prompts)
            if dump_prompts:
                logger.debug(f"Number of prompts: {len(prompts)}")
                for prompt in prompts:
                    logger.debug('prompt: %s', prompt)

            # for resource in self.resource_list:
            #     print(resource)

            # 'ucm-mcp://ucm_mcp/file-content/{filepath*}'

            # read_resource_responses = await self.mcp_client.read_resource('ucm-mcp://ucm_mcp/file-content/C:/Code/zong/pft/aws/agents/README.md')
            # print('read_resource_responses', read_resource_responses)
            # 'file://C:/Code/zong/pft/aws/agents/README.md')



            # read_resource_responses = await self.mcp_client.read_resource('ucm-mcp://ucm_mcp/local-file')
            # print('read_resource_responses', read_resource_responses)

            # self._initialize_chat_prompt(self.resource_list)

            # read_resource_responses = await self.mcp_client.read_resource("ucm-mcp://ucm_mcp/counter-name")
            # resource_list = self._handle_read_resource_responses(read_resource_responses)

            # print('resource_list', resource_list)
            # for resource in resource_list:
            #     read_resource_responses = await self.mcp_client.read_resource(f"ucm-mcp://ucm_mcp/counter/{resource}")
            #     rsrc = self._handle_read_resource_responses(read_resource_responses)
            #     print('rsrc', rsrc)

            # resource = 'testCounter1'
            # read_resource_responses = await self.mcp_client.read_resource(f"ucm-mcp://ucm_mcp/counter/{resource}")
            # rsrc = self._handle_read_resource_responses(read_resource_responses)
            # print('rsrc', rsrc)

            # get_prompt(name: str, arguments: dict[str, Any] | None = None):
            # prompt_response = await self.mcp_client.get_prompt(
            #     'ucm_mcp_InitializeQuery', {
            #         "mcp_resources": "\n".join([ str(resource) for resource in self.resource_list ]),
            #         "query": "What resources can I access?"
            #     })
            # print(f'\nPROMPT RESPONSE: {prompt_response}')
            # print(f'Number of messages: {len(prompt_response.messages)}')
            # prompt_message = prompt_response.messages[0]
            # print('\nPROMPT:')
            # # prompt_message.content is TextContent
            # print(prompt_message.content.text)
            #
        if dump_connect:
            logger.debug("Client connected: %s", self.mcp_client.is_connected())

    async def async_initialize(self):
        # Initialize session and client objects
        # self.session: Optional[ClientSession] = None
        # self.exit_stack = AsyncExitStack()
        await self._initialize_tools()
        self._initialize_chat()

    def _get_tool_call_response_content(self, response_list):
        """
        response (list[mcp.types.TextContent | mcp.types.ImageContent | ...])
        [TextContent(type='text', text='17', annotations=None)]
        """
        text_content_list = []
        for response in response_list:
            response_class_name = response.__class__.__name__.lower()
            match response_class_name:
                case 'textcontent':
                    text_content_list.append(response.text)
                case _:
                    logger.warning('Unhandled tool call response type: %s', response_class_name)

        return " ".join(text_content_list)


    async def _handle_chat_completion_response(self, response):
        """Handler for openai.types.chat.chat_completion.ChatCompletion
        ChatCompletion response message which looks like:
        ChatCompletion(
            id='chatcmpl-6d9e0801-c9aa-44c1-96d7-71e416aefa27',
            choices=[
                Choice(
                    finish_reason='stop',
                    index=0,
                    logprobs=None,
                    message=ChatCompletionMessage(content='Hello! How can I help you today?\n',
                        refusal=None,
                        role='assistant',
                        annotations=None,
                        audio=None,
                        function_call=None,
                        tool_calls=None
                    )
                )
            ],
            created=1749004825,
            model='gemini-1.5-flash-002',
            object='chat.completion',
            service_tier=None,
            system_fingerprint=None,
            usage=CompletionUsage(
                completion_tokens=10,
                prompt_tokens=28,
                total_tokens=38,
                completion_tokens_details=None,
                prompt_tokens_details=PromptTokensDetails(
                    audio_tokens=None,
                    cached_tokens=None
                )
            ),
            vertex_ai_grounding_metadata=[],
            vertex_ai_safety_results=[],
            vertex_ai_citation_metadata=[])
        """
        number_of_choices = len(response.choices)
        logger.debug("Number of choices in ChatCompletion: %d", number_of_choices)
        for choice in response.choices:
            logger.debug("Choice: %s", choice)

        chosen_message = None
        finish_reason = None
        if number_of_choices <= 1:
            chosen_message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason.lower()
        else:
            # Have yet to encounter a case where we got multiple choices
            logger.error('Unhandled multiple choices: %s', response)
            raise NotImplementedError()

        match finish_reason:
            case 'stop':

                if chosen_message.content.startswith('READ_RESOURCE:'):
                    resource_uri = chosen_message.content.replace('READ_RESOURCE:', '').strip().strip('.')
                    async with self.mcp_client:
                        pdb.set_trace()
                        read_resource_responses = await self.mcp_client.read_resource(resource_uri)
                        resource_list = self._handle_read_resource_responses(read_resource_responses)

                else:
                    chat_response = {
                        "role": chosen_message.role,
                        "content": chosen_message.content
                    }
                    self.message_history.append(chat_response)
                    return chat_response
            case 'tool_calls':
                for tool_call in chosen_message.tool_calls: # tool_call is type: ChatCompletionMessageToolCall
                    chosen_response_role = chosen_message.role
                    tool_call_function = tool_call.function

                    async with self.mcp_client:
                        tool_call_result_list = await self.mcp_client.call_tool(tool_call_function.name, json.loads(tool_call_function.arguments))
                        tool_call.response = tool_call_result_list
                        # # result -> list[mcp.types.TextContent | mcp.types.ImageContent | ...]
                        # logger.debug('Result of tool call %s:\n%s', tool_call_function.name, tool_call_result_list)
                        # # Interpret tool_call_result_list
                        # for tool_call_result in tool_call_result_list:
                        #     self.message_history.append({
                        #         "type": "tool_result",
                        #         "tool_use_id": tool_call.id,
                        #         "content": tool_call_result_list[0].text
                        #     })
                # In event of multiple tool calls, how should we handle it?
                # For lack of sophistication, just pick the first one.
                # Note: It could very be that tool_calls should combine somehow to form a more logical response.
                first_tool_call = chosen_message.tool_calls[0]
                tool_call_response_content = self._get_tool_call_response_content(first_tool_call.response)

                self.message_history.append({
                    "type": "tool_result",
                    "tool_use_id": first_tool_call.id,
                    "content": tool_call_response_content
                })
                chat_response = {
                    "role": chosen_response_role,
                    "content": tool_call_response_content
                }
                return chat_response
            case _:
                logger.warning('Unhandled finish_reason: %s', finish_reason)

    async def get_chat_response(self, query: str) -> str:

        self.message_history.append({
            "role": "user",
            "content": query
        })

        if self._use_synaptic:
            response = await self.chat_client.chat.completions.create(
                model=self.llm_model,
                messages=self.message_history,
                tools=self.tools
            )
            logger.debug('Chat completion response: %s', response)
            # handle response by class name
            response_class_name = response.__class__.__name__.lower()
            match response_class_name:
                case 'chatcompletion':
                    return await self._handle_chat_completion_response(response)
                case _:
                    logger.warning("Unable to handle %s:\n%s", response_class_name, response)
        else:
            logger.warning("MISSING IMPLEMENTATION")
            # Initial Claude API call
            # response = self.anthropic.messages.create(
            #     model="claude-3-5-sonnet-20241022",
            #     max_tokens=1000,
            #     messages=messages,
            #     tools=available_tools
            # )
        return None

    async def start_chat(self):
        """Runs an interactive chat loop"""
        # print("Type 'quit' to exit.\n")
        # counter = 0
        # while True:
        #     time.sleep(1)
        #     counter = counter + 1
        #     print(f'Waited {counter} s')
        # Get directory (ucm-mcp://ucm_mcp/file-list/{directory_path*})

        # We get target_directory somewhere
        target_directory = 'C:/Code/zong/pft/aws/cinema'

        async with (self.mcp_client):
            read_resource_responses = await self.mcp_client.read_resource(f'ucm-mcp://ucm_mcp/file-list/{target_directory}')
            parsed_response = self._handle_read_resource_responses(read_resource_responses)
            print('parsed_response', parsed_response)
            if len(parsed_response) <= 0:
                return
            first_parsed_response = parsed_response[0]
            filename_list = first_parsed_response['files'] if 'files' in first_parsed_response else []

            import os
            print('Filenames: ', len(filename_list))

            for filename in filename_list:
                file_path = os.path.normpath(os.path.join(target_directory, filename))
                file_path.replace('\\', '/')
                split_ext = os.path.splitext(file_path)

                file_name = split_ext[0]
                file_extension = split_ext[1].lower()
                if file_name.startswith('.') or file_extension in ['.json', '']:
                    print(f'Skipping {file_path}')
                    continue
                print(f"To get content of {file_path} and then do something with it")
                # Read the file
                read_resource_responses = await self.mcp_client.read_resource(f'ucm-mcp://ucm_mcp/file-content/{file_path}')
                print('read_resource_responses', read_resource_responses)
                parsed_response = self._handle_read_resource_responses(read_resource_responses)

                prompt_response = await self.mcp_client.get_prompt(
                    'ucm_mcp_ReviewCode', {
                        "code": parsed_response
                    })
                # print(f'\nPROMPT RESPONSE: {prompt_response}')
                # print(f'Number of messages: {len(prompt_response.messages)}')
                prompt_message = prompt_response.messages[0]
                # prompt_message.content is TextContent
                print('PROMPT:', prompt_message.content.text)
                # pdb.set_trace()
                query = prompt_message.content.text
                response = await self.get_chat_response(query)
                print(query)
                print('response', response['content'])
                with open('C:/Code/zong/pft/aws/cinema/review/review.md', 'w', encoding='utf8') as out_file:
                    out_file.write(response['content'])
                return




        # while True:
        #     try:
        #         query = input(f"[{len(self.message_history):03}]{'USER':>4}: ").strip()
        #         if query.lower() == 'quit':
        #             break
        #         if len(query) <= 0:
        #             continue
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
    mcp_config = McpClientJsonConfiguration('./conduit_mcp_client.json')
    fast_mcp_client = FastMcpClient(mcp_config)
    await fast_mcp_client.async_initialize()
    await fast_mcp_client.async_debug_dump()
    await fast_mcp_client.start_chat()

if __name__ == "__main__":
    asyncio.run(main())