"""API
Sections:
    AWS PROFILE SETUP
    GENERAL HTTP-RELATED STUFF
    END-POINT RELATED STUFF
    END POINTS
"""
import json
from os import environ

from shared_lambda import (
    endpoint_url,
    dump_api_gateway_event_context,
    EndpointResponse,
    EventBodyJson)

# from hci_decorators import endpoint_url, dump_api_gateway_event_context
# from hci_messages import HciMessageService
# from hci_message_queues import HciMessageQueue

# hci_message_service = HciMessageService()
# hci_message_queue = HciMessageQueue()

# AWS PROFILE SETUP

# runtime_dns_domain = environ.get('USERDNSDOMAIN')
# aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
# boto3.setup_default_session(profile_name=aws_profile)


# GENERAL HTTP-RELATED STUFF

endpoint_response = EndpointResponse()


# END POINTS

## Authentication

@endpoint_url('/ucm/authenticate-ticket', 'POST')
def post_ucm_authenticate_ticket(event:dict, context):
    """Authenticate credentials to get an authentication ticket to use with app
    Use case:
        (authentication)
    """
    dump_api_gateway_event_context(event, context)


## User Credential

@endpoint_url('/ucm/user-credential', 'GET')
def get_ucm_user_credential(event:dict, context):
    """List user credentials
    Use case:
        (list user credentials)
    """
    dump_api_gateway_event_context(event, context)


## Membership

@endpoint_url('/ucm/membership', 'GET')
def get_ucm_membership(event:dict, context):
    """List memberships
    Use case:
        (list memberships)
    """
    dump_api_gateway_event_context(event, context)


# from hci_inventory_item import InventoryItemRepository
# repository = InventoryItemRepository()


# @endpoint_url('/hci-blazer/item', 'GET')
# def get_hci_blazer_item(event:dict, context):
#     dump_api_gateway_event_context(event, context)
#
#     # event_body_json = __get_event_body_json(event)
#     # if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.ErrorMessage)
#
#     try:
#         operation_result = repository.get_all_inventory_item()
#
#         ep_response = endpoint_response.data(operation_result)
#
#         return ep_response
#     except Exception as err:
#         print(err)


# @endpoint_url('/ucm/item', 'POST')
# def post_hci_blazer_item(event:dict, context):
#     """Receive create new inventory item messages
#     Use case:
#         (register new item)
#     """
#     event_body_json = EventBodyJson.get_event_body_json(event)
#
#     if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.ErrorMessage)
#
#     new_inventory_item_message = hci_message_service.create_new_inventory_item_message(event_body_json.DataObject)
#
#     if new_inventory_item_message is None: return endpoint_response.bad_request('Invalid new inventory item message')
#
#     operation_result = repository.add_new_inventory_item(new_inventory_item_message)
#
#     return_message = f'{new_inventory_item_message.item_code} added successfully' if operation_result.is_success else f'{new_inventory_item_message.item_code} fail to add'
#
#     return endpoint_response.ok(operation_result.is_success, return_message)


def main():
    pass

if __name__ == "__main__":
    main()
