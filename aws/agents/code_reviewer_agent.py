import asyncio
import json
import os
import mcp
from fastmcp import Client
from shared_mcp import (
    get_mcp_client_logger,
    McpClientJsonConfiguration,
    FastMcpClient,
    FileUtility,
)

import pdb

logger = get_mcp_client_logger()

class ConduitFastMcpClient(FastMcpClient):
    def __init__(self, mcp_config: McpClientJsonConfiguration):
        super().__init__(mcp_config)

    def _get_chat_client(self, preferred_llm: str = 'gemini-1.5-flash-002'):
        if self._use_synaptic:
            from conduit_client import AsyncOpenAI
            client = AsyncOpenAI()
            client.model = preferred_llm
            return client
        raise RuntimeError('NO DEFINED CHAT CLIENT')

    def _get_system_prompt(self):
        mcp_resources = "\n".join(map(str, self.resource_list))
        add_instructions = """
        If the query requires reading MCP resources and making tool calls from given MCP resources:
        1. If resource is not in given MCP resources list, prefix the name with 'TO-IMPLEMENT'.
        2. Respond as:    
        ```
        {
          tasks: [
            {
              "action": "read_resource",
              "explain": <text description>,
              "resource": <MCP RESOURCE URI>
            },
            {
              "action": "tool_call",
              "explain": <text description>,
              "name": <TOOL_NAME>,
                  "description": <TOOL_DESCRIPTION>,
                  "parameters": <TOOL_INPUT_SCHEMA>
                }
              ]
            }
        ```
        """
        seed_prompt = f"You are a world-class software engineer.\n\nGiven following MCP resources:\n\n```\n{mcp_resources}\n```\n\n{add_instructions}"
        self.message_history.append({"role": "system", "content": seed_prompt})
        return "You are a world-class software engineer."

    def _handle_read_resource_responses(self, responses):
        resource_list = []
        for response in responses:
            class_name = response.__class__.__name__.lower()
            if class_name == 'textresourcecontents':
                if response.mimeType == 'application/json':
                    resource = json.loads(response.text)
                    if isinstance(resource, dict):
                        resource_list.append(resource)
                    elif isinstance(resource, list):
                        resource_list.extend(resource)
                    else:
                        logger.warning('Unhandled resource type: %s', type(resource).__name__)
                elif response.mimeType == 'text/plain':
                    return response.text
            else:
                logger.warning('Unhandled response type: %s', class_name)
        return resource_list

    def _get_tool_call_response_content(self, responses):
        text_content_list = [
            response.text for response in responses if response.__class__.__name__.lower() == 'textcontent'
        ]
        return " ".join(text_content_list)

    async def _handle_chat_completion_response(self, response):
        if len(response.choices) != 1:
            logger.error('Unhandled response: %s', response)
            raise NotImplementedError()

        chosen_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason.lower()

        if finish_reason == 'stop':
            if chosen_message.content.startswith('READ_RESOURCE:'):
                resource_uri = chosen_message.content.replace('READ_RESOURCE:', '').strip().strip('.')
                async with self.mcp_client:
                    responses = await self.mcp_client.read_resource(resource_uri)
                    self.resource_list = self._handle_read_resource_responses(responses)
            else:
                chat_response = {"role": chosen_message.role, "content": chosen_message.content}
                self.message_history.append(chat_response)
                return chat_response
        elif finish_reason == 'tool_calls':
            first_tool_call = chosen_message.tool_calls[0]
            async with self.mcp_client:
                responses = await self.mcp_client.call_tool(
                    first_tool_call.function.name, json.loads(first_tool_call.function.arguments)
                )
                first_tool_call.response = responses
            tool_call_response_content = self._get_tool_call_response_content(first_tool_call.response)
            self.message_history.append({"type": "tool_result", "tool_use_id": first_tool_call.id, "content": tool_call_response_content})
            return {"role": chosen_message.role, "content": tool_call_response_content}
        else:
            logger.warning('Unhandled finish_reason: %s', finish_reason)

    async def _process_chat_response(self, query: str) -> str:
        self.message_history.append({"role": "user", "content": query})
        if self._use_synaptic:
            response = await self.chat_client.chat.completions.create(
                model=self.llm_model, messages=self.message_history, tools=self.tools
            )
            if response.__class__.__name__.lower() == 'chatcompletion':
                return await self._handle_chat_completion_response(response)
            logger.warning("Unable to handle response: %s", response)
        else:
            logger.warning("Missing implementation for non-synaptic chat clients")
        return None

    def _is_in_skip_list(self, file_name: str) -> bool:
        file_name, file_extension = FileUtility.get_file_path_parts(file_name)
        return file_name.startswith('.') or file_extension in ['.json', '', '.png']

    def _get_review_file_name(self, original_file_name: str) -> str:
        return f"{original_file_name}.review.md"

    async def start_chat(self, target_directory: str = 'C:/Code/zong/pft/aws/cinema'):
        review_output_directory = os.path.normpath(f'{target_directory}_code_review')
        os.makedirs(review_output_directory, exist_ok=True)

        async with self.mcp_client:
            normalized_dir = FileUtility.normalize_path(directory_path=target_directory)
            responses = await self.mcp_client.read_resource(f'ucm-mcp://file-list/{normalized_dir}')
            parsed_response = self._handle_read_resource_responses(responses)
            if not parsed_response:
                return

            filename_list = parsed_response[0].get('files', [])
            for filename in filename_list:
                normalized_path = FileUtility.normalize_path(normalized_dir, filename)
                base_name = os.path.basename(normalized_path)
                dir_name = os.path.dirname(filename)

                if self._is_in_skip_list(base_name):
                    continue

                os.makedirs(os.path.join(review_output_directory, dir_name), exist_ok=True)
                review_file_path = os.path.join(review_output_directory, dir_name, self._get_review_file_name(base_name))
                if os.path.exists(review_file_path):
                    logger.info('Skipping existing review file: %s', review_file_path)
                    continue

                # Ensure parent directory exists for the review file
                os.makedirs(os.path.dirname(review_file_path), exist_ok=True)

                responses = await self.mcp_client.read_resource(f'ucm-mcp://file-content/{normalized_path}')
                parsed_response = self._handle_read_resource_responses(responses)
                prompt_response = await self.mcp_client.get_prompt('ReviewCode', {"code": parsed_response})
                query = prompt_response.messages[0].content.text
                response = await self._process_chat_response(query)

                with open(review_file_path, 'w', encoding='utf8') as out_file:
                    out_file.write(response['content'])

async def main():
    mcp_config = McpClientJsonConfiguration('./code_reviewer_agent_config.json')
    fast_mcp_client = ConduitFastMcpClient(mcp_config)
    await fast_mcp_client.initialize_mcp_resource_list(dump_resource_list=False)
    fast_mcp_client.initialize_chat(fast_mcp_client._get_chat_client(), None)
    await fast_mcp_client.start_chat(target_directory = 'C:/Code/zong/pft/aws/s3/emptool-public')

if __name__ == "__main__":
    asyncio.run(main())
