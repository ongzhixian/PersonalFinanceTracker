import logging
import json
import os
from datetime import datetime
from collections import Counter


# LOGGING RELATED

def get_logger(logger_name: str = None):
    # default_format = "\n[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    default_format = "%(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    message_centric_format = "[%(levelname).3s] %(message)s"
    # default_format = message_centric_format
    logging.basicConfig(
        level=logging.INFO,
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


# CONFIGURATION RELATED

def get_config_or_exit(script_path: str = None):
    filepath = os.path.abspath(__file__) if script_path is None else script_path
    filename_wo_ext = os.path.splitext(os.path.basename(filepath))[0]
    config_filename = f"{filename_wo_ext}-config.json"
    config_filepath = os.path.join(os.path.dirname(filepath), config_filename)
    with open(config_filepath, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigProperty:
    type: str = "string"
    description: str = "Description of the configuration property"
    value: any = None


def get_config_property(property_name: str, config: dict) -> ConfigProperty:
    prop = config.get(property_name)
    if not prop:
        raise KeyError(f"Configuration property '{property_name}' not found.")
    return ConfigProperty(
        type=prop.get('type', 'string'),
        description=prop.get('description', 'Description of the configuration property'),
        value=prop.get('value', prop.get('default', None))
    )


# SESSION RELATED

def get_session_id():
    return f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}'


# I/O RELATED

def create_directory_if_not_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


# LLM RELATED

class LlmClient():
    def __init__(self, model_name: str, use_synaptic: bool = True):
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
