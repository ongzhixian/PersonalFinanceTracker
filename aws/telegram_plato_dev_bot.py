# Handler to pass Slack Event Request Url verification

import json
import http.client
import logging
from os import environ

def send_message(chat_id: str, message: str):
    running_on_aws_lambda = 'LAMBDA_TASK_ROOT' in environ

    bot_api_token = environ['bot_api_token'] if 'bot_api_token' in environ else None

    if bot_api_token is None:
        logging.warning('bot_api_token is not defined in environment variables; send_message does nothing.')
        return

    if running_on_aws_lambda:
        conn = http.client.HTTPSConnection('api.telegram.org')
    else:
        proxy_host = 'siproxyvip.ad.mlp.com'
        proxy_port = 3128
        conn = http.client.HTTPConnection(proxy_host, proxy_port)

    headers = {
        'Content-type': 'application/json; charset=utf-8',
    }

    body = json.dumps({
        'chat_id': chat_id,
        'text': message
    })

    conn.request(method="POST",
                 url=f"https://api.telegram.org/{bot_api_token}/sendMessage",
                 body=body,
                 headers=headers)

    response = conn.getresponse()
    print("Status:", response.status, response.reason)
    data = response.read()
    print("Response body:", data.decode())
    conn.close()



def lambda_handler(event, context):
    print("event", event)       # event(type) <class 'dict'>
    print("context", context)   # context(type) <class 'awslambdaric.lambda_context.LambdaContext'>

    if 'body' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('`body` not found in event')
        }

    body = event['body']
    print('body', body)

    jsonBody = json.loads(body)
    print('jsonBody', jsonBody)

    # if 'chat' not in jsonBody:
    #     return {
    #         'statusCode': 400,
    #         'body': json.dumps('`event` not found in JSON body')
    #     }

    message = jsonBody['message'] if 'message' in jsonBody else None
    if message is None:
        message = jsonBody['edited_message'] if 'edited_message' in jsonBody else None

    if message is None:
        return {
            'statusCode': 400,
            'body': json.dumps('`message` or `edited_message` not found in JSON body')
        }

    if 'chat' not in message:
        return {
            'statusCode': 400,
            'body': json.dumps('`chat` not found in JSON body (message)')
        }

    message_chat = message['chat']

    if 'id' not in message_chat:
        return {
            'statusCode': 400,
            'body': json.dumps('`id` not found in JSON body (message_chat)')
        }

    reply_chat_id = message_chat['id']
    #reply_channel = data_event['channel']

    if 'text' not in message:
        return {
            'statusCode': 400,
            'body': json.dumps('`text` not found in JSON body (message)')
        }
    message_text = message['text']

    send_message(reply_chat_id, f'Echoing {message_text}')

    return {
        'statusCode': 200,
        # 'body': json.dumps('Return from Lambda')
    }


if __name__ == "__main__":
    send_message('D08AERL1CRE', 'send some reply')