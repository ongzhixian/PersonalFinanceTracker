import json
import requests

def lambda_handler(event, context):
    print("[event]", event)
    print("[context]", context)

    request_headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer xxxx'
    }
    webhook_url = 'https://hooks.slack.com/services/TXXX/BXXX/XXX'
    request_data = {
        'text': 'Some test message'
    }

    #r = requests.post(webhook_url, json=request_data, headers=request_headers)
    response = requests.post(webhook_url, data=json.dumps(request_data), headers=request_headers)
    if response.ok:
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent succeed')
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('Message sent failed')
    }
    
    

if __name__ == "__main__":
    print("Working")
    lambda_handler(None, None)
    # https://flikx8i3c2.execute-api.us-east-1.amazonaws.com/hci-blazer/test-request