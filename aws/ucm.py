"""API
Sections:
    AWS PROFILE SETUP
    GENERAL HTTP-RELATED STUFF
    END-POINT RELATED STUFF
    END POINTS
"""

from shared_lambda import (
    endpoint_url,
    dump_api_gateway_event_context,
    EndpointResponse,
    EventBodyJson,
    EventHeadersJson)
from shared_messages import OperationResultMessage
from shared_user_credential_messages import AddUserCredentialMessage, AuthenticateUserCredentialMessage
from shared_user_credential import UserCredentialRepository
from shared_configuration import ConfigurationRepository
from utility_types import TokenUtility
from shared_token_service import SharedTokenService

# AWS PROFILE SETUP

# runtime_dns_domain = environ.get('USERDNSDOMAIN')
# aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
# boto3.setup_default_session(profile_name=aws_profile)


# GENERAL HTTP-RELATED STUFF

# END POINTS

endpoint_response = EndpointResponse()

shared_token_service = SharedTokenService()

## Authentication

# def generate_token():
#     configuration_repository = ConfigurationRepository()
#     operation_result_message = configuration_repository.get_configuration('UCM_SECRETS')
#     if 'content' not in operation_result_message.data_object: return None
#     content = operation_result_message.data_object['content']
#
#     if 'authentication_token' not in content: return None
#     authentication_token = content['authentication_token']
#
#     if 'value' not in authentication_token: return None
#     secret_key =  authentication_token['value']
#     token_utility = TokenUtility(secret_key)
#     new_token = token_utility.generate_token(60 * 60)
#     return new_token
#
# class SharedTokenService(object):
#     def __init__(self):
#         pass


@endpoint_url('/ucm/authentication-ticket', 'POST')
def post_ucm_authentication_ticket(event:dict, context):
    """Authenticate credentials to get an authentication ticket to use with app
    Use case:
        (authentication)
    """
    dump_api_gateway_event_context(event, context)

    # Validation

    # EventHeadersJson.get_event_headers_json(event)
    authorization_header = EventHeadersJson.get_authorization_header(event)
    if authorization_header is None:
        return endpoint_response.forbidden()

    event_body_json = EventBodyJson.get_event_body_json(event)
    if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

    authenticate_user_credential_message = AuthenticateUserCredentialMessage.create_from_dict(event_body_json.data_object)
    if authenticate_user_credential_message is None: return endpoint_response.bad_request('Invalid authenticate user credential message')

    # Repository action

    repository = UserCredentialRepository()
    operation_result_message = repository.authenticate_user_credential(authenticate_user_credential_message)

    return_message = f'{authenticate_user_credential_message.username} added successfully' if operation_result_message.is_success else f'{authenticate_user_credential_message.username} fail to add'

    token = shared_token_service.generate_token()
    return endpoint_response.data(OperationResultMessage(
        operation_is_successful=operation_result_message.is_success,
        message=return_message,
        data_object={
            'token' : token
        }))


## User Credential

@endpoint_url('/ucm/user-credential', 'GET')
def get_ucm_user_credential(event:dict, context):
    """List user credentials
    Use case:
        (list user credentials)
    """
    return dump_api_gateway_event_context(event, context)

@endpoint_url('/ucm/user-credential', 'POST')
def post_ucm_user_credential(event:dict, context):
    """Create user credentials if validation passes
    Use case:
        (create user credential)
    """
    dump_api_gateway_event_context(event, context)

    # Validation

    authorization_header = None
    if 'headers' in event:
        headers = event['headers']
        if 'authorization' in headers:
            authorization_header = headers['authorization']

    event_body_json = EventBodyJson.get_event_body_json(event)
    if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

    add_user_credential_message = AddUserCredentialMessage.create_from_dict(event_body_json.data_object)
    if add_user_credential_message is None: return endpoint_response.bad_request('Invalid add user credential message')

    # Repository action

    repository = UserCredentialRepository()
    operation_result = repository.add_user_credential(add_user_credential_message)

    return_message = f'{add_user_credential_message.username} added successfully' if operation_result.is_success else f'{add_user_credential_message.username} fail to add'
    return endpoint_response.ok(operation_result.is_success, return_message)

    # operation_result_message = OperationResultMessage(
    #     operation_is_successful=True,
    #     message='User credential added.',
    #     data_object= {
    #         'username': 'simu',
    #         'status': 'ok'
    #     })
    # return endpoint_response.data(operation_result_message)


## Membership

@endpoint_url('/ucm/membership', 'GET')
def get_ucm_membership(event:dict, context):
    """List memberships
    Use case:
        (list memberships)
    """
    return dump_api_gateway_event_context(event, context)



## Configuration

@endpoint_url('/ucm/configuration', 'GET')
def get_ucm_configuration(event:dict, context):
    """Get configuration
    Use case:
        (get configuration)
    """
    return dump_api_gateway_event_context(event, context)




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
