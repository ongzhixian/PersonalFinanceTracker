"""API
Sections:
    AWS PROFILE SETUP
    AWS Setup DynamoDB
    GENERAL HTTP-RELATED STUFF
    END-POINT RELATED STUFF
    END POINTS
"""
import json
from os import environ
from datetime import datetime, timezone, timedelta

import boto3
import botocore.exceptions


import pdb

# AWS PROFILE SETUP

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
boto3.setup_default_session(profile_name=aws_profile)


# AWS Setup DynamoDB

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')


# GENERAL HTTP-RELATED STUFF


class EndpointResponse(object):
    """Encapsulates logic endpoint outgoing responses"""
    def __init__(self):
        self.HTTP_OK_CODE = 200
        self.HTTP_BAD_REQUEST_CODE = 400

    def response(self, http_code:int, body_text:str) -> dict:
        return {
            'statusCode': http_code,
            'body': json.dumps(body_text)
        }

    # def bad_request(self, text_message:str) -> dict:
    #     return ResponseMessage(
    #         self.HTTP_BAD_REQUEST_CODE,
    #         json.dumps(OperationResultMessage(False, text_message).__dict__)).to_dict()
    #
    # def ok(self, is_success:bool, return_message:str) -> dict:
    #     return ResponseMessage(
    #         self.HTTP_OK_CODE,
    #         json.dumps(OperationResultMessage(is_success, return_message).__dict__)).to_dict()

endpoint_response = EndpointResponse()


# END-POINT RELATED STUFF

class EventBodyJson(object):
    """Parsed result of an API Gateway event body"""
    def __init__(self, data_object:dict|None = None, error_message:str|None = None):
        """
        Args:
            data_object (dict|none): Data object result of parsing event object
            error_message (str|none): An error message to indicate where parsing failed
        """
        self.DataObject = data_object
        self.ErrorMessage = error_message
        self.is_invalid = self.DataObject is None

    def __str__(self):
        return f"is_invalid:{not self.is_invalid}, ErrorMessage:{self.ErrorMessage}, DataObject:{self.DataObject}"

def __get_event_body_json(event:dict):
    """Parses an API Gateway event object to return EventJsonBody
    Args:
        event (dict): Event object received from API Gateway
    Returns:
        EventBodyJson: Result from parsing event arg
    """
    if 'body' not in event:
        return EventBodyJson(error_message='`body` not found in context')

    try:
        return EventBodyJson(data_object=json.loads(event['body']))
    except json.decoder.JSONDecodeError:
        return EventBodyJson(error_message='`body` is invalid json')

def dump_api_gateway_event_context(event:dict, context):
    ''' Prints the event and context that AWS API Gateway receives
    Args:
        event (dict): The ID of the item to retrieve.
        context (str, optional): An optional query parameter.
    Returns:
        response (dict): object with status code and text message
    '''
    print("[event]", event)
    print("[context]", context)
    return {
        'statusCode': 200,
        'body': json.dumps('Successful HTTP')
    }


# END POINTS

#@endpoint_url('/hci-blazer/auth', 'POST')
def dump_request(event:dict, context):
    """Dumps api gateway request"""
    dump_api_gateway_event_context(event, context)

#@endpoint_url('/hci-blazer/auth', 'POST')
def sample_write_google_sheet(event:dict, context):
    """Appends data to a Google sheet
    Use case:
        (authentication)
    """
    print('Step 1')
    dump_api_gateway_event_context(event, context)
    try:
        print('Step 2')
        from sample_google_sheet import GoogleSheet
        spreadsheet_id = '1IeETC6g8xqipia0SnrMsXOxN14SONPZxmJVOWx_rHgY'
        sheet_name = 'Outstanding'
        print('Step 3')
        data_to_add = [
            # ['New Data A1', 'New Data B1', 'New Data C1'],
            # ['Another Row 1', 'Another Row 2']
            ['item 1', 'Some student 2', '2025-05-10', '2025-05-24']
        ]
        print('Step 4')
        google_sheet = GoogleSheet(spreadsheet_id)
        print('Step 5')
        google_sheet.append_to_sheet(sheet_name, data_to_add)
        return {
            'statusCode': 200,
            'body': json.dumps('Successful HTTP OK')
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': f"{e}"
        }

def __write_to_google_sheet(data_to_add):
    from sample_google_sheet import GoogleSheet
    spreadsheet_id = '1IeETC6g8xqipia0SnrMsXOxN14SONPZxmJVOWx_rHgY'
    sheet_name = 'Outstanding'
    google_sheet = GoogleSheet(spreadsheet_id)
    google_sheet.append_to_sheet(sheet_name, data_to_add)
    return {
        'statusCode': 200,
        'body': json.dumps('Successful HTTP OK')
    }

def sample_sqs_handler(event:dict, context):
    try:
        # Do interesting work based on the new message
        dump_api_gateway_event_context(event, context)
        for record in event['Records']:
            body = json.loads(record['body'])
            __write_to_google_sheet(body)
            print(f"Message body: {body}")
    except Exception as err:
        print("An error occurred")
        print(err)
        #raise err

def sample_sns_handler(event:dict, context):
    dump_api_gateway_event_context(event, context)


if __name__ == "__main__":
    pass

    # post_hci_blazer_item({
    #     "body": ''
    # }, None)
    # post_hci_blazer_item({
    #     "body": json.dumps({
    #         "key1": 'key1-value',
    #         "key2": 'key2-value',
    #         "key3": 'key3-value',
    #     })
    # }, None)

#     import sys
#     if len(sys.argv) < 2:
#         print(sys.argv)
#         print (len(sys.argv))
#         raise Exception('Too little arguments')
#     print(globals()[sys.argv[1]].__doc__)