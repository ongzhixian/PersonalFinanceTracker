import argparse
import asyncio
import json
import os
import re
from collections import Counter
from datetime import datetime

from common_utilities import create_directory_if_not_exists, get_logger, get_config_or_exit, get_config_property, get_session_id

import pdb


logger = get_logger()

class LlmClient():
    def __init__(self, model_name:str, use_synaptic: bool = True):
        self.use_synaptic = use_synaptic
        self.init_message_history()

        if use_synaptic:
            from conduit_client import AsyncOpenAI
            self.client = AsyncOpenAI()
            self.client.model = model_name
            return
        raise RuntimeError('NO DEFINED CHAT CLIENT')

    def init_message_history(self):
        self.message_history = []
        self.message_history.append({
            "role": "system",
            "content": 'You are a world-class software engineer.'
        })

    async def get_supported_model_list(self):
        response = await self.client.models.list()
        model_list = response.data
        print("Supported models count:", len(model_list))

        owned_by_count = Counter(model.owned_by for model in model_list)
        for owner, count in owned_by_count.items():
            print(f"Owner: {owner:>25}, Count: {count:>2}")

        for model in model_list:
            if model.owned_by == "synaptic-completion":
                print(f"Model: {model.owned_by}: {model.id} ")

    def set_model(self, model_name: str):
        self.client.model = model_name

    async def get_chat_response(self, message: str, reset_history: bool = False):
        if reset_history:
            self.init_message_history()
        self.message_history.append({
            "role": "user",
            "content": message
        })
        response = await self.client.chat.completions.create(
            model=self.client.model,
            messages=self.message_history
        )

        response_choice_count = len(response.choices)
        if response_choice_count > 1:
            return f"Unexpected number of choices: {len(response.choices)}"
        response = response.choices[0].message
        self.message_history.append({
            "role": response.role,
            "content": response.content
        })

        return response.content


def save_files_from_llm_response(response: str, output_dir: str = "."):
    create_directory_if_not_exists(output_dir)
    # Pattern matches: **Filename: <relative/path/to/filename>** ... ```<lang>\n<content>\n```
    pattern = r'\*\*Filename:\s*([^\*]+?)\*\*\s*```(?:[^\n]*)\n([\s\S]+?)```'
    matches = re.findall(pattern, response)
    for filename, content in matches:
        filepath = os.path.join(output_dir, filename.strip())
        directory = os.path.dirname(filepath)
        if directory:
            create_directory_if_not_exists(directory)
        try:
            print(f"Saving to: {filepath}")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"Saved: {filepath}")
        except Exception as e:
            print(f"Error saving {filepath}: {e}")


def get_prompt_from_argument_or_exit():
    parser = argparse.ArgumentParser(description="LLM prompt file")
    parser.add_argument('--prompt-file', '-p', type=str, help='Path to the prompt file')
    args = parser.parse_args()
    logger.info("Prompt file provided: %s", args.prompt_file)

    if args.prompt_file is None:
        logger.error("No prompt file provided. Exiting.")
        exit(-1)

    with open(args.prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read().strip()
        if not prompt:
            logger.error("Prompt file is empty.")
            exit(-1)
        logger.info("Prompt loaded.")
        return prompt


def find_sql_files_location(target_stored_proc_file: str, sql_files_location: str):
    for root, _, files in os.walk(sql_files_location):
        if target_stored_proc_file in files:
            target_file_path = os.path.join(root, target_stored_proc_file)
            if os.path.isfile(target_file_path):
                logger.info(f"Found {target_stored_proc_file} at {target_file_path}")
                return target_file_path
            break
    logger.error(f"{target_stored_proc_file} not found in {sql_files_location}. Exiting.")
    return None


async def main():
    config = get_config_or_exit(script_path=__file__)
    sql_files_location = get_config_property('sql_files_location', config)
    llm_model = get_config_property('llm', config)
    prompt = get_prompt_from_argument_or_exit()
    session_id = get_session_id()

    target_stored_proc_file = 'xxx.sql'
    target_stored_proc_file = 'xxx.sql'
    sql_file_location = find_sql_files_location(target_stored_proc_file, sql_files_location.value)

    if not sql_file_location:
        logger.error(f"SQL file location for {target_stored_proc_file} not found.")
        return
    
    with open(sql_file_location, 'r', encoding='utf-8') as f:
        sql_content = f.read().strip()
        if not sql_content:
            logger.error(f"SQL file {target_stored_proc_file} is empty.")
            return
        
    full_prompt = f"{prompt}\n\nSQL Content:\n```sql\n{sql_content}\n```"
    # print('sql_content:', sql_content)
    llm_client = LlmClient(llm_model.value)
    chat_response = await llm_client.get_chat_response(full_prompt)
    with open(f'chat_response-{session_id}.md', 'w', encoding='utf-8') as f:
        f.write(chat_response)
    # print('\nChat response:', chat_response)
    output_dir = f'output-{session_id}'
    save_files_from_llm_response(chat_response, output_dir)


if __name__ == "__main__":
    """This is the main entry point for the script.
    Run instructions: python.exe .\agent.py -p .\prompts\gen-website.md
    """
    asyncio.run(main())
    