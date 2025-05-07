import os
import json
from google import genai
from google.genai import types
import os
import requests

def get_secrets_dict():
    user_secrets_id = 'tech-notes-press'
    user_secrets_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json')
    with open(user_secrets_path) as input_file:
        return json.load(input_file)
    return {}

def send_simple_message(mailgun_api_key:str):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox47c34c75284a4686854c434ad041fcce.mailgun.org/messages",
        auth=("api", mailgun_api_key),
        data={"from": "Mailgun Sandbox <postmaster@sandbox47c34c75284a4686854c434ad041fcce.mailgun.org>",
              "to": "Ong Zhi Xian <zhixian@hotmail.com>",
              "subject": "Hello Ong Zhi Xian",
              "text": "Congratulations Ong Zhi Xian, you just sent an email with Mailgun! You are truly awesome!"})

if __name__ == '__main__':
    secrets = get_secrets_dict()
    if 'hci_blazer_gemini_api_key' not in secrets.keys():
        print('`hci_blazer_gemini_api_key` is not defined secret; exiting...')
        exit(1)
    mailgun_api_key = secrets['test_mailgun_api_key']
    print('mailgun_api_key', mailgun_api_key)
    response = send_simple_message(mailgun_api_key)
    print(response)