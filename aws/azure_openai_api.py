import json
import os
from openai import AzureOpenAI, azure_endpoint


def get_secrets_dict():
    user_secrets_id = 'tech-notes-press'
    user_secrets_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json')
    with open(user_secrets_path) as input_file:
        return json.load(input_file)
    return {}

if __name__ == '__main__':
    secrets = get_secrets_dict()

    if 'azure_openai_api_key' not in secrets.keys():
        print('`azure_openai_api_key` is not defined secret; exiting...')
        exit(1)
    azure_openai_api_key = secrets['azure_openai_api_key']
    azure_endpoint = 'https://eastus.api.cognitive.microsoft.com/'

    # if 'azure_hci_rg_openai' not in secrets.keys():
    #     print('`azure_hci_rg_openai` is not defined secret; exiting...')
    #     exit(1)
    # azure_openai_api_key = secrets['azure_hci_rg_openai']
    # azure_endpoint = 'https://hci-rg-openai.openai.azure.com/'

    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_openai_api_key,
        api_version="2024-02-01"
    )

    response = client.chat.completions.create(
        model="gpt-35-turbo",  # model = "deployment_name".
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
            {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
            {"role": "user", "content": "Do other Azure services support this too?"}
        ]
    )

    print(response.choices[0].message.content)