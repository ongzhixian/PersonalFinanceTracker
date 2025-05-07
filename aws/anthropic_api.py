import os
import json
from google import genai
from google.genai import types
import anthropic

def get_secrets_dict():
    user_secrets_id = 'tech-notes-press'
    user_secrets_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json')
    with open(user_secrets_path) as input_file:
        return json.load(input_file)
    return {}


if __name__ == '__main__':
    secrets = get_secrets_dict()
    if 'anthropic_api_key' not in secrets.keys():
        print('`anthropic_api_key` is not defined secret; exiting...')
        exit(1)
    anthropic_api_key = secrets['anthropic_api_key']
    # print(anthropic_api_key)
    # exit(1)

    client = anthropic.Anthropic(api_key=anthropic_api_key)

    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=1,
        system="You are a world-class poet. Respond only with short poems.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Why is the ocean salty?"
                    }
                ]
            }
        ]
    )
    print(message.content)
