import json
import os
from openai import OpenAI

def get_secrets_dict():
    user_secrets_id = 'tech-notes-press'
    user_secrets_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json')
    with open(user_secrets_path) as input_file:
        return json.load(input_file)
    return {}

if __name__ == '__main__':
    secrets = get_secrets_dict()
    if 'openai_api_key' not in secrets.keys():
        print('`openai_api_key` is not defined secret; exiting...')
        exit(1)
    openai_api_key = secrets['openai_api_key']

    client = OpenAI(api_key=openai_api_key)

    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a coding assistant that talks like a pirate.",
        input="How do I check if a Python object is an instance of a class?",
    )

    print(response.output_text)