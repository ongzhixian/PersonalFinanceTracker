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

import boto3

from hci_decorators import endpoint_url, dump_api_gateway_event_context
from shared_messages import OperationResultMessage, ResponseMessage
from hci_messages import HciMessageService
from hci_message_queues import HciMessageQueue

hci_message_service = HciMessageService()
hci_message_queue = HciMessageQueue()

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

    # def response(self, http_code:int, body_text:str) -> dict:
    #     return {
    #         'statusCode': http_code,
    #         'body': json.dumps(body_text)
    #     }

    def bad_request(self, text_message:str) -> dict:
        return ResponseMessage(
            self.HTTP_BAD_REQUEST_CODE,
            json.dumps(OperationResultMessage(False, text_message).__dict__)).to_dict()

    def ok(self, is_success:bool, return_message:str) -> dict:
        return ResponseMessage(
            self.HTTP_OK_CODE,
            json.dumps(OperationResultMessage(is_success, return_message).__dict__)).to_dict()

    def data(self, operation_result_message:OperationResultMessage) -> dict:
        return ResponseMessage(
            self.HTTP_OK_CODE,
            json.dumps(operation_result_message.__dict__)
        ).to_dict()

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


# END POINTS

@endpoint_url('/hci-blazer/auth', 'POST')
def post_hci_blazer_auth(event:dict, context):
    """Authenticate credentials to get an authentication ticket to use with app
    Use case:
        (authentication)
    """
    dump_api_gateway_event_context(event, context)


from hci_inventory_item import InventoryItemRepository
repository = InventoryItemRepository()


@endpoint_url('/hci-blazer/item', 'GET')
def get_hci_blazer_item(event:dict, context):
    dump_api_gateway_event_context(event, context)

    # event_body_json = __get_event_body_json(event)
    # if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.ErrorMessage)

    try:
        operation_result = repository.get_all_inventory_item()

        ep_response = endpoint_response.data(operation_result)

        return ep_response
    except Exception as err:
        print(err)


@endpoint_url('/hci-blazer/item', 'POST')
def post_hci_blazer_item(event:dict, context):
    """Receive create new inventory item messages
    Use case:
        (register new item)
    """
    event_body_json = __get_event_body_json(event)

    if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.ErrorMessage)

    new_inventory_item_message = hci_message_service.create_new_inventory_item_message(event_body_json.DataObject)

    if new_inventory_item_message is None: return endpoint_response.bad_request('Invalid new inventory item message')

    operation_result = repository.add_new_inventory_item(new_inventory_item_message)

    return_message = f'{new_inventory_item_message.item_code} added successfully' if operation_result.is_success else f'{new_inventory_item_message.item_code} fail to add'

    return endpoint_response.ok(operation_result.is_success, return_message)


@endpoint_url('/hci-blazer/item', 'PATCH')
def patch_hci_blazer_item(event:dict, context):
    """Receive borrow / extend borrows / return inventory item messages
    Use case:
        (borrow item) -
        (return item) -
        (extend borrow item) - KIV
    """
    dump_api_gateway_event_context(event, context)

    event_body_json = __get_event_body_json(event)

    if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.ErrorMessage)

    update_inventory_item_message = hci_message_service.create_update_inventory_item_message(event_body_json.DataObject)

    if update_inventory_item_message is None: return endpoint_response.bad_request('Invalid borrow inventory item message')

    operation_result = repository.update_inventory_item(update_inventory_item_message)

    #return_message = f'{update_inventory_item_message.item_code} borrowed successfully' if operation_result.is_success else f'{update_inventory_item_message.item_code} fail to borrow'
    return_message = operation_result.message

    if operation_result.is_success:
        # Item Code, Borrower, Borrow Date, Due Date
        print('data_object', operation_result.data_object)
        hci_message_queue.enqueue_hci_blazer_google_sheet_update_message(
            update_inventory_item_message.update_type,
            json.dumps(operation_result.data_object)
        )

    return endpoint_response.ok(operation_result.is_success, return_message)


@endpoint_url('/hci-blazer/item', 'DELETE')
def delete_hci_blazer_item(event:dict, context):
    """WHY_WE_NEED_THIS_METHOD
    Use case:
        (some use case)
    """
    dump_api_gateway_event_context(event, context)

@endpoint_url('/hci-blazer/item/{id}', 'GET')
def patch_hci_blazer_item_id(event:dict, context):
    """WHY_WE_NEED_THIS_METHOD
    Use case:
        (some use case)
    """
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