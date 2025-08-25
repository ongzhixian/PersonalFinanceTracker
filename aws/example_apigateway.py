import boto3

# Create an API Gateway client
# apigateway_client = boto3.client('apigateway')
apigateway_client = boto3.client('apigatewayv2')


def display_api_list():
    response = apigateway_client.get_apis()
    print(response)
    api_list = response.get('Items', [])
    for api in api_list:
        print(f"API ID: {api['ApiId']}, API Name: {api['Name']}, Protocol Type: {api['ProtocolType']}")


def create_api():
    api_name = "MyBoto3HttpApi"
    response_api = apigateway_client.create_api(
        Name=api_name,
        ProtocolType='HTTP',
        # Target="arn:aws:lambda:REGION:ACCOUNT_ID:function:YOUR_LAMBDA_FUNCTION_NAME", # Replace with your Lambda ARN
        Description="An HTTP API created with Boto3"
    )
    api_id = response_api['ApiId']
    print(f"HTTP API created with ID: {api_id}")

def main():
    pass
    # create_api()
    display_api_list()
    # TODO: Add CORS configuration to an existing API


    # List all REST APIs    
    # print("APIs:")
    # for api in apis['items']:
    #     print(f" - {api['name']} (ID: {api['id']})")

if __name__ == '__main__':
    main()