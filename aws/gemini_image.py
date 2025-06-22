import os
import json
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

def get_secrets_dict():
    user_secrets_id = 'tech-notes-press'
    user_secrets_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json')
    with open(user_secrets_path) as input_file:
        return json.load(input_file)
    return {}


if __name__ == '__main__':
    secrets = get_secrets_dict()
    if 'hci_blazer_gemini_api_key' not in secrets.keys():
        print('`hci_blazer_gemini_api_key` is not defined secret; exiting...')
        exit(1)
    gemini_api_key = secrets['hci_blazer_gemini_api_key']
    # gen(gemini_api_key)
    # print(response)
    client = genai.Client(api_key=gemini_api_key)

    contents = ('Hi, can you create a 3d rendered image of a pig '
                'with wings and a top hat flying over a happy '
                'futuristic scifi city with lots of greenery?')

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
          response_modalities=['TEXT', 'IMAGE']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save('gemini-native-image.png')
            # image.show()
