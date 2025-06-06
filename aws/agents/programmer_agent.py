import asyncio
import json
import os
import time
import pdb

import mcp
from fastmcp import Client

from shared_mcp import get_mcp_client_logger, McpClientJsonConfiguration, FastMcpClient, FileUtility

logger = get_mcp_client_logger()

########################################

class ConduitFastMcpClient(FastMcpClient):

    def __init__(self, mcp_config: McpClientJsonConfiguration):
        super().__init__(mcp_config)

    def _get_chat_client(self, preferred_llm:str='gemini-1.5-flash-002'):
        if self._use_synaptic:  # Use Conduit
            from conduit_client import AsyncOpenAI
            client = AsyncOpenAI()
            client.model = preferred_llm
            return client
        else:
            raise RuntimeError('NO DEFINED CHAT CLIENT')
            return None

    def _get_system_prompt(self):
        """
        Attempt to work around MCP limitations by giving ability to read resources.
        This currently goes against the way MCP wants to work...so KIV and go tool_call oriented.
        """
        mcp_resources = "\n".join([str(resource) for resource in self.resource_list])
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
        seed_prompt = f"You are a world-class software engineer."
        return seed_prompt

    def _handle_read_resource_responses(self, read_resource_responses):
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
        if number_of_choices <= 0 or number_of_choices > 1: # We want to know when there are multiple Choices available for us
            logger.debug("Number of choices in ChatCompletion: %d", number_of_choices)
            for choice in response.choices:
                logger.debug("Choice: %s", choice)
            # Have yet to encounter a case where we got multiple choices
            logger.error('Unhandled response: %s', response)
            raise NotImplementedError()

        # We are only able to handle a single Choice for now.
        chosen_message = chosen_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason.lower()

        match finish_reason:
            case 'stop':
                if chosen_message.content.startswith('READ_RESOURCE:'): # HACK-ish
                    resource_uri = chosen_message.content.replace('READ_RESOURCE:', '').strip().strip('.')
                    async with self.mcp_client:
                        read_resource_responses = await self.mcp_client.read_resource(resource_uri)
                        self.resource_list = self._handle_read_resource_responses(read_resource_responses)
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

                # Track history and return a response suitable for display to console
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

    async def _process_chat_request(self, query: str) -> str:

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
            # Conduit will return an object of ChatCompletion
            match response_class_name:
                case 'chatcompletion':
                    return await self._handle_chat_completion_response(response)
                case _:
                    logger.warning("Unable to handle %s:\n%s", response_class_name, response)
        else:
            logger.warning("Missing implementation for non-synaptic chat clients")
        return None

    def _is_in_skip_list(self, file_name: str) -> bool:
        (file_name, file_extension) = FileUtility.get_file_path_parts(file_name)
        if file_name.startswith('.') or file_extension in ['.json', '']:
            return True
        return False

    def _get_review_file_name(self, original_file_name: str) -> str:
        return f"{original_file_name.replace('.', '_')}_review.md"

    def _parse_xml_string(self, xml_string):
        pass
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_string)

        # Parse code files
        for code_file in root.find('codeFileList').findall('codeFile'):
            filename = code_file.get('filename')
            code = code_file.find('code').text.strip()
            description = code_file.find('description').text.strip()
            print(f'Filename: {filename}')
            print(f'Description: {description}')
            print('Code:')
            print(code)
            print('---')

        # Parse summary
        summary = root.find('summary').text.strip()
        print('Summary:', summary)

    def _remove_code_fences(self, markdown: str) -> str:
        """
        Remove code fences (``` or ~~~) from a markdown string.
        Keeps the code content, removes the fence lines.
        """
        import re
        # Pattern matches lines starting with ``` or ~~~ (optionally followed by language)
        pattern = re.compile(r'^\s*(```|~~~).*$', re.MULTILINE)
        return re.sub(pattern, '', markdown)

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
        target_directory = 'C:/Code/zong/pft/aws/agents/specs'

        # Given target_directory
        # 1. Get list of files in target_directory
        # 2. For each file, get content
        # 3. Create code review prompt for content
        # 4. Send prompt to LLM
        # 5. Save response from LLM

        async with (self.mcp_client):
            normalized_file_directory = FileUtility.normalize_path(directory_path=target_directory)
            read_resource_responses = await self.mcp_client.read_resource(f'ucm-mcp://ucm_mcp/file-list/{normalized_file_directory}')
            parsed_response = self._handle_read_resource_responses(read_resource_responses)
            if len(parsed_response) <= 0:
                return
            first_parsed_response = parsed_response[0]
            filename_list = first_parsed_response['files'] if 'files' in first_parsed_response else []

            print('Filenames: ', len(filename_list))

            for filename in filename_list:
                normalized_file_path = FileUtility.normalize_path(normalized_file_directory, filename)
                print('normalized_file_path', normalized_file_path)

                normalized_file_name = os.path.basename(normalized_file_path)
                if self._is_in_skip_list(normalized_file_name):
                    print(f'Skipping {normalized_file_path}')
                    continue

                # Read the file
                print(f"Processing {normalized_file_path}")
                read_resource_responses = await self.mcp_client.read_resource(f'ucm-mcp://ucm_mcp/file-content/{normalized_file_path}')
                parsed_response = self._handle_read_resource_responses(read_resource_responses)

                # Create prompt for code review.
                prompt_response = await self.mcp_client.get_prompt(
                    'ucm_mcp_GeneratePythonCode', {
                        "specification": parsed_response
                    })
                # print(f'Number of messages: {len(prompt_response.messages)}')
                prompt_message = prompt_response.messages[0]
                query = prompt_message.content.text

                query = f"""Given:
```specification.md
Generate a dog class and a cat class.
```

Generate Python code.
Respond in XML structure as plain text (do not use any markdown or code block notation):
<response mimetype="text/xml">
  <codeFileList>
    <codeFile filename="FILENAME">
        <code>CODE AS PLAIN TEXT</code>
        <description>DESCRIPTION OF GENERATED CODE</description>
    </codeFile>
    ...
  </codeFileList>
  <summary>
    SUMMARY OF GENERATED RESPONSE
  </summary>
</response>
```

Separate each class into separate file.
"""

                # Run query
                response = await self._process_chat_request(query)
                print('RESPONSE:', response)
                code_file_name_path = os.path.join(normalized_file_directory, '_code_review', self._get_review_file_name(normalized_file_name))
                code_file_name_path = f'C:/Code/zong/pft/aws/agents/_temp/spec-{time.strftime("%Y%m%d%H%M%S")}.xml'
                # parsed_content = self._remove_code_fences(response['content']).strip()
                # print('parsed_content:', parsed_content)
                parsed_content = response['content']
                with open(code_file_name_path, 'w', encoding='utf8') as out_file:
                    out_file.write(parsed_content)
                self._parse_xml_string(parsed_content)
                return


async def main():
    mcp_config = McpClientJsonConfiguration('./programmer_agent_config.json')
    fast_mcp_client = ConduitFastMcpClient(mcp_config)
    await fast_mcp_client.initialize_mcp_resource_list(dump_resource_list=False)
    # Add customizations
    chat_client = fast_mcp_client._get_chat_client()
    system_prompt = fast_mcp_client._get_system_prompt()
    system_prompt = 'You are a world-class software engineer.'
    fast_mcp_client.initialize_chat(chat_client, system_prompt)
    await fast_mcp_client.start_chat()


if __name__ == "__main__":
    asyncio.run(main())