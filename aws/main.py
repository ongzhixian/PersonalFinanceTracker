import json

def lambda_handler(event, context):
    print("Event")
    print(event)
    print("context")
    print(context)
    return {
        'statusCode': 200,
        'body': json.dumps('Return from Lambda')
    }