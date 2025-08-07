import asyncio
import re
from collections import Counter

from shared_mcp import get_mcp_client_logger

import pdb

logger = get_mcp_client_logger()

########################################

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
    # Pattern matches: Filename: <filename> ... ```<lang>\n<content>\n```
    pattern = r'Filename:\s*(\S+)\s+```(?:\w+)?\s*([\s\S]+?)```'
    matches = re.findall(pattern, response)
    for filename, content in matches:
        filepath = f"{output_dir}/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Saved: {filepath}")



async def main():
    from datetime import datetime
    session_id = f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    llm_client = LlmClient('gemini-2.5-flash')
    # model_list = await llm_client.get_supported_model_list()
    # llm_client.set_model('gemini-2.5-flash')
    # chat_response = await llm_client.get_chat_response('How are you?')
    # print('\nChat response:', chat_response)
    # chat_response = await llm_client.get_chat_response('Generate a website that use webcomponents for managing a application list.')
    # chat_response = await llm_client.get_chat_response(
    #     'How to profile memory usage of .net core application?')
    #
    # print('\nChat response:', chat_response)
    # with open(f'chat_response-{session_id}.txt', 'w') as f:
    #     f.write(chat_response)
    # chat_response = await llm_client.get_chat_response('Generate a website that use webcomponents for managing a application list.')
    chat_response = await llm_client.get_chat_response(
        '''Write a simple website with a landing page and a contact form. Use webcomponents for the contact form.
        Output the result as:
        Filename: <filename>
        <code block with language>''', )

    with open(f'chat_response-{session_id}.txt', 'w', encoding='utf-8') as f:
        f.write(chat_response)
    # print('\nChat response:', chat_response)
    save_files_from_llm_response(chat_response, 'output')

if __name__ == "__main__":
    asyncio.run(main())