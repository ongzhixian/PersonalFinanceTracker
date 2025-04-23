# Handler to pass Slack Event Request Url verification

import json
import http.client
import logging
from os import environ


def send_message(channel: str, message: str):
    running_on_aws_lambda = 'LAMBDA_TASK_ROOT' in environ

    bot_token = environ['bot_token'] if 'bot_token' in environ else None

    if bot_token is None:
        logging.warning('bot_token is not defined in environment variables; send_message does nothing.')
        return

    if running_on_aws_lambda:
        conn = http.client.HTTPSConnection('slack.com')
    else:
        proxy_host = 'siproxyvip.ad.mlp.com'
        proxy_port = 3128
        conn = http.client.HTTPConnection(proxy_host, proxy_port)

    headers = {
        'Content-type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {bot_token}'
    }

    body = json.dumps({
        'channel': channel,
        'text': message
    })
    conn.request(method="POST",
                 url="https://slack.com/api/chat.postMessage",
                 body=body,
                 headers=headers)

    response = conn.getresponse()
    print("Status:", response.status, response.reason)
    data = response.read()
    print("Response body:", data.decode())
    conn.close()


def lambda_handler(event, context):
    print("event", event)
    # print("context", context)
    # print("event(type)", type(event))     # event(type) <class 'dict'>
    # print("context(type)", type(context)) # context(type) <class 'awslambdaric.lambda_context.LambdaContext'>

    if 'body' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('`body` not found in event')
        }

    body = event['body']
    print('body', body)

    jsonBody = json.loads(body)
    print('jsonBody', jsonBody)

    if 'event' not in jsonBody:
        return {
            'statusCode': 400,
            'body': json.dumps('`event` not found in JSON body')
        }

    bot_user_id = environ['bot_user_id'] if 'bot_user_id' in environ else None
    # bot_token = environ['bot_token']
    # bot_version = environ['version']

    data_event = jsonBody['event']
    print('data_event', data_event)

    user_id = data_event['user'] if 'user' in data_event else None
    if user_id is None:
        return

    if bot_user_id is None or bot_user_id == user_id:
        return

    reply_channel = data_event['channel']
    message_text = data_event['text']

    send_message(reply_channel, f'Echoing {message_text}')

    return {
        'statusCode': 200,
        # 'body': json.dumps('Return from Lambda')
    }


if __name__ == "__main__":
    send_message('D08AERL1CRE', 'send some reply')