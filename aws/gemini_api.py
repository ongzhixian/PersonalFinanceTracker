import os
import json
from google import genai
from google.genai import types

def get_secrets_dict():
    user_secrets_id = 'tech-notes-press'
    user_secrets_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json')
    with open(user_secrets_path) as input_file:
        return json.load(input_file)
    return {}

def gen(gemini_api_key:str):
    client = genai.Client(api_key=gemini_api_key)
    chat_history = []
    user_input = input("YOU: ")
    if user_input == 'exit':
        exit(0)
    chat_history.append(user_input)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction="You are a cat. Your name is Neko."),
        contents=["Hello there"]
    )
    print(response)


if __name__ == '__main__':
    secrets = get_secrets_dict()
    if 'hci_blazer_gemini_api_key' not in secrets.keys():
        print('`hci_blazer_gemini_api_key` is not defined secret; exiting...')
        exit(1)
    gemini_api_key = secrets['hci_blazer_gemini_api_key']
    gen(gemini_api_key)
    # print(response)