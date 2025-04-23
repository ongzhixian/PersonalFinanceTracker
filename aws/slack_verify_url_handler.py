# Handler to pass Slack Event Request Url verification

import json


def lambda_handler(event, context):
    print("event", event)
    print("context", context)
    # print("event(type)", type(event))     # event(type) <class 'dict'>
    # print("context(type)", type(context)) # context(type) <class 'awslambdaric.lambda_context.LambdaContext'>

    if 'body' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('`body` not found in context')
        }

    body = event['body']
    print('body', body)

    jsonBody = json.loads(body)
    print('jsonBody', jsonBody)

    challenge = jsonBody['challenge']
    print('jsonBody', challenge)

    return challenge
    return {
        'statusCode': 200,
        'body': json.dumps('Return from Lambda')
    }