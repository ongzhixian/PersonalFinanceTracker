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
    EventHeadersJson,
    EventQueryStringParametersJson,
    EventPathParametersJson)
from shared_messages import OperationResultMessage
from shared_user_credential_messages import AddUserCredentialMessage, AuthenticateUserCredentialMessage
from shared_user_credential import UserCredentialRepository
from shared_role_messages import AddRoleMessage
from shared_role import RoleRepository
from shared_configuration import ConfigurationRepository
from shared_notification import Notification
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

    try:
        # Validation
        print('# Request Validation Phase')

        # print('## Check authorization header')
        #
        # # EventHeadersJson.get_event_headers_json(event)
        # authorization_header = EventHeadersJson.get_authorization_header(event)
        # if authorization_header is None:
        #     return endpoint_response.forbidden()

        print('## Event body retrieval')

        event_body_json = EventBodyJson.get_event_body_json(event)
        if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

        print('## Generating message from event body')

        authenticate_user_credential_message = AuthenticateUserCredentialMessage.create_from_dict(event_body_json.data_object)
        if authenticate_user_credential_message is None: return endpoint_response.bad_request('Invalid authenticate user credential message')

        # Repository action
        print('# Repository Action Phase')

        repository = UserCredentialRepository()
        operation_result_message = repository.authenticate_user_credential(authenticate_user_credential_message)

        if operation_result_message.is_success:
            # If success, we should have a data object
            credential_check_result = operation_result_message.data_object
            is_valid_credential = credential_check_result['is_valid']
            credential_check_message = credential_check_result['message']

            print('## POST authenticate_user_credential', operation_result_message)
            # return_message = f'{authenticate_user_credential_message.username} credential validated.' if is_valid_credential else f'{authenticate_user_credential_message.username} credential are invalid.'

            # token = shared_token_service.generate_token() if is_valid_credential else None
            data_object = {
                'token': shared_token_service.generate_token(authenticate_user_credential_message.username),
                'username': authenticate_user_credential_message.username,
            } if is_valid_credential else None

            return endpoint_response.data(OperationResultMessage(
                operation_is_successful=operation_result_message.is_success,
                message=credential_check_message,
                data_object=data_object))

        return endpoint_response.bad_gateway(operation_result_message)
    except Exception as error:
        print(error)
        return endpoint_response.ok(False, f'HAS ERROR: {error}')


@endpoint_url('/ucm/authentication-ticket', 'PUT')
def put_ucm_authentication_ticket(event:dict, context):
    """Refreshes a token (given a valid token)
    Use case:
        (authentication)
    """
    dump_api_gateway_event_context(event, context)

    try:
        # Validation
        print('# Request Validation Phase')

        authorization_header = EventHeadersJson.get_authorization_header(event)
        if authorization_header is None:
            return endpoint_response.forbidden()

        token_body = authorization_header.replace('TOKEN', '').strip()
        token_is_valid = shared_token_service.verify_token(token_body)
        if not token_is_valid:
            return endpoint_response.forbidden()

        # Parse the token to get the username
        username = shared_token_service.get_token_content(token_body)

        data_object = {
            'token': shared_token_service.generate_token(username )
        }

        return endpoint_response.data(OperationResultMessage(
                operation_is_successful=True,
                message='Token refreshed.',
                data_object=data_object))

    except Exception as error:
        print(error)
        return endpoint_response.ok(False, f'HAS ERROR: {error}')

## User Credential

def access_denied(event: dict, target_roles:list[str] = []):
    """Validates access to endpoint.
    Use case:
        (validate access)
    """
    print('Checking access to endpoint...')
    authorization_header = EventHeadersJson.get_authorization_header(event)
    if authorization_header is None:
        print('MISSING authorization_header')
        return True

    token_body = authorization_header.replace('TOKEN', '').strip()
    # token_is_valid = shared_token_service.verify_token(token_body)
    # if not token_is_valid:
    #     print('INVALID token')
    #     return True

    # token_content = shared_token_service.get_token_content(token_body)
    # print('Token content:', token_content)

    has_target_roles = shared_token_service.verify_token_has_roles(token_body, target_roles=target_roles)
    print('Has target roles:', has_target_roles)
    return False if has_target_roles else True


def get_query_string_parameters(event: dict, target_parameters: dict):
    """Get query string parameters from event.
    Use case:
        (get query string parameters)
    """
    event_query_string_parameters_json = EventQueryStringParametersJson.get_event_query_string_parameters_json(event)
    if not event_query_string_parameters_json.is_valid:
        print('MISSING or INVALID query string parameters')
        return ()
    print("Start checking")
    query_param_dict = {}
    query_string_parameters = event_query_string_parameters_json.data_object
    print('Query string parameters:', query_string_parameters)
    for query_param_k, query_param_v in query_string_parameters.items():
        print('Query parameter:', query_param_k, 'with default value:', query_param_v)
        query_param_dict[query_param_k] = query_string_parameters.get(query_param_k, query_param_v)
    print('Query parameters:', query_param_dict)
    return tuple(query_param_dict)
    # page_number = int(query_param_dict.get('page_number', target_parameters['page_number']))
    # page_size = int(query_param_dict.get('page_size', target_parameters['page_size']))
    # return (page_number, page_size)
    # return (target_parameters['page_number'], target_parameters['page_size'])

@endpoint_url('/ucm/user-credential', 'GET')
def get_ucm_user_credential(event:dict, context):
    """List user credentials
    Use case:
        (list user credentials)
    """
    dump_api_gateway_event_context(event, context)

    try:
        # Validation
        # print('# Request Validation Phase')

        # print('## Check authorization header')

        # authorization_header = EventHeadersJson.get_authorization_header(event)
        # if authorization_header is None:
        #     return endpoint_response.forbidden()

        # print('## Validating token')

        # token_body = authorization_header.replace('TOKEN', '').strip()
        # token_is_valid = shared_token_service.verify_token(token_body)
        # if not token_is_valid:
        #     return endpoint_response.forbidden()


        #print('## Event body retrieval')
        #event_body_json = EventBodyJson.get_event_body_json(event)
        #if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

        if access_denied(event, target_roles=['application_administrator', 'system_administrator']):
            return endpoint_response.forbidden()


        print('## Query String Parameters')
        (page_number, page_size) = get_query_string_parameters(event, {
            'page_number' : 1,
            'page_size': 6})

        print('Page number:', page_number, 'Page size:', page_size)

        page_number = 1
        page_size = 5

        event_query_string_parameters_json = EventQueryStringParametersJson.get_event_query_string_parameters_json(event)
        if event_query_string_parameters_json.is_valid:
            print('event_query_string_parameters_json.is_valid')
            query_string_parameters = event_query_string_parameters_json.data_object
            page_number = int(query_string_parameters.get('page_number', 1))
            page_size = int(query_string_parameters.get('page_size', 5))

        # print('## Generating message from event body')
        # authenticate_user_credential_message = AuthenticateUserCredentialMessage.create_from_dict(event_body_json.data_object)
        # if authenticate_user_credential_message is None: return endpoint_response.bad_request('Invalid authenticate user credential message')

        # Repository action
        print('# Repository Action Phase')

        repository = UserCredentialRepository()
        operation_result_message = repository.get_user_credential_list(page_size=page_size, page_number=page_number)

        if operation_result_message.is_success:
            return endpoint_response.data(operation_result_message)
        return endpoint_response.bad_gateway(operation_result_message)
    except Exception as error:
        print(error)
        return endpoint_response.ok(False, f'HAS ERROR: {error}')

@endpoint_url('/ucm/user-credential', 'POST')
def post_ucm_user_credential(event:dict, context):
    """Create user credentials if validation passes
    Use case:
        (create user credential)
    """
    dump_api_gateway_event_context(event, context)

    # Validation

    print('# Request Validation Phase')

    # Old style
    # authorization_header = EventHeadersJson.get_authorization_header(event)
    # if authorization_header is None:
    #     return endpoint_response.forbidden()

    # token_body = authorization_header.replace('TOKEN', '').strip()
    # token_is_valid = shared_token_service.verify_token(token_body)
    # if not token_is_valid:
    #     return endpoint_response.forbidden()
    
    if access_denied(event, target_roles=['application_administrator', 'system_administrator']):
        return endpoint_response.forbidden()

    # authorization_header = None
    # if 'headers' in event:
    #     headers = event['headers']
    #     if 'authorization' in headers:
    #         authorization_header = headers['authorization']

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

@endpoint_url('/ucm/user-credential/{0}', 'GET')
def get_ucm_user_credential_record(event: dict, context):
    """List user credentials
    Use case:
        (list user credentials)
    """
    dump_api_gateway_event_context(event, context)

    try:
        # Validation
        print('# Request Validation Phase')

        print('## Check authorization header')

        # authorization_header = EventHeadersJson.get_authorization_header(event)
        # if authorization_header is None:
        #     print('MISSING authorization_header')
        #     return endpoint_response.forbidden()
        #
        # token_body = authorization_header.replace('TOKEN', '').strip()
        # token_is_valid = shared_token_service.verify_token(token_body)
        # if not token_is_valid:
        #     print('INVALID token')
        #     return endpoint_response.forbidden()

        # print('## Event body retrieval')
        # event_body_json = EventBodyJson.get_event_body_json(event)
        # if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)
        username = None
        print('## Query String Parameters')
        event_query_string_parameters_json = EventQueryStringParametersJson.get_event_query_string_parameters_json(event)
        if event_query_string_parameters_json.is_valid:
            print('event_query_string_parameters_json.is_valid')
            query_string_parameters = event_query_string_parameters_json.data_object
            print(query_string_parameters)
            username = str(query_string_parameters.get('id', None))
            print('Query params for username %s', username)

        path_parameters_json = EventPathParametersJson.get_event_path_parameters_json(event)
        if path_parameters_json.is_valid:
            print('path_parameters_json.is_valid')
            path_parameters = path_parameters_json.data_object
            print(path_parameters)
            username = str(path_parameters.get('id', None))
            print('path_parameters for username %s', username)

        print('Final username %s', username)

        # print('## Generating message from event body')
        # authenticate_user_credential_message = AuthenticateUserCredentialMessage.create_from_dict(event_body_json.data_object)
        # if authenticate_user_credential_message is None: return endpoint_response.bad_request('Invalid authenticate user credential message')

        # Repository action
        print('# Repository Action Phase')

        repository = UserCredentialRepository()
        operation_result_message = repository.get_user_credential(username=username)

        if operation_result_message.is_success:
            return endpoint_response.data(operation_result_message)
        return endpoint_response.bad_gateway(operation_result_message)
    except Exception as error:
        print(error)
        return endpoint_response.ok(False, f'HAS ERROR: {error}')


## Membership

@endpoint_url('/ucm/membership', 'GET')
def get_ucm_membership(event:dict, context):
    """List memberships
    Use case:
        (list memberships)
    """
    return dump_api_gateway_event_context(event, context)

@endpoint_url('/ucm/membership', 'POST')
def post_ucm_membership(event:dict, context):
    """Add membership
    Use case:
        (add membership)
    """
    return dump_api_gateway_event_context(event, context)

@endpoint_url('/ucm/user-membership', 'POST')
def post_ucm_user_membership(event:dict, context):
    """Add user membership
    Use case:
        (add user membership)
    """
    return dump_api_gateway_event_context(event, context)

@endpoint_url('/ucm/user-membership', 'DELETE')
def delete_ucm_user_membership(event:dict, context):
    """Delete user membership
    Use case:
        (delete user membership)
    """
    return dump_api_gateway_event_context(event, context)


## Role

@endpoint_url('/ucm/role', 'GET')
def get_ucm_role(event:dict, context):
    """List roles
    Use case:
        (list roles)
    """
    dump_api_gateway_event_context(event, context)

    try:
        # Validation
        print('# Request Validation Phase')
        print('## Check authorization header')

        authorization_header = EventHeadersJson.get_authorization_header(event)
        if authorization_header is None:
            return endpoint_response.forbidden()

        token_body = authorization_header.replace('TOKEN', '').strip()
        token_is_valid = shared_token_service.verify_token(token_body)
        if not token_is_valid:
            return endpoint_response.forbidden()

        # print('## Event body retrieval')
        # event_body_json = EventBodyJson.get_event_body_json(event)
        # if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

        print('## Query String Parameters')

        page_number = 1
        page_size = 5

        event_query_string_parameters_json = EventQueryStringParametersJson.get_event_query_string_parameters_json(
            event)
        if event_query_string_parameters_json.is_valid:
            print('event_query_string_parameters_json.is_valid')
            query_string_parameters = event_query_string_parameters_json.data_object
            page_number = int(query_string_parameters.get('page_number', 1))
            page_size = int(query_string_parameters.get('page_size', 5))

        # print('## Generating message from event body')
        # authenticate_user_credential_message = AuthenticateUserCredentialMessage.create_from_dict(event_body_json.data_object)
        # if authenticate_user_credential_message is None: return endpoint_response.bad_request('Invalid authenticate user credential message')

        # Repository action
        print('# Repository Action Phase')

        repository = RoleRepository()
        operation_result_message = repository.get_role_list()

        if operation_result_message.is_success:
            return endpoint_response.data(operation_result_message)
        return endpoint_response.bad_gateway(operation_result_message)
    except Exception as error:
        print(error)
        return endpoint_response.ok(False, f'HAS ERROR: {error}')

@endpoint_url('/ucm/role', 'POST')
def add_ucm_role(event:dict, context):
    """List roles
    Use case:
        (list roles)
    """
    dump_api_gateway_event_context(event, context)

    try:
        # Validation
        print('# Request Validation Phase')
        print('## Check authorization header')

        # authorization_header = EventHeadersJson.get_authorization_header(event)
        # if authorization_header is None:
        #     return endpoint_response.forbidden()

        # token_body = authorization_header.replace('TOKEN', '').strip()
        # token_is_valid = shared_token_service.verify_token(token_body)
        # if not token_is_valid:
        #     return endpoint_response.forbidden()

        print('## Event body retrieval')
        event_body_json = EventBodyJson.get_event_body_json(event)
        if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

        # print('## Query String Parameters')

        # page_number = 1
        # page_size = 5

        # event_query_string_parameters_json = EventQueryStringParametersJson.get_event_query_string_parameters_json(
        #     event)
        # if event_query_string_parameters_json.is_valid:
        #     print('event_query_string_parameters_json.is_valid')
        #     query_string_parameters = event_query_string_parameters_json.data_object
        #     page_number = int(query_string_parameters.get('page_number', 1))
        #     page_size = int(query_string_parameters.get('page_size', 5))

        print('## Generating message from event body')

        add_role_message = AddRoleMessage.create_from_dict(event_body_json.data_object)
        if add_role_message is None: return endpoint_response.bad_request('Invalid add role message')

        # Repository action
        print('# Repository Action Phase')

        repository = RoleRepository()
        repository.add_role(add_role_message)
        operation_result_message = repository.get_role_list()

        if operation_result_message.is_success:
            return endpoint_response.data(operation_result_message)
        return endpoint_response.bad_gateway(operation_result_message)
    except Exception as error:
        print(error)
        return endpoint_response.ok(False, f'HAS ERROR: {error}')

@endpoint_url('/ucm/role', 'DELETE')
def remove_ucm_role(event:dict, context):
    """List roles
    Use case:
        (list roles)
    """
    return dump_api_gateway_event_context(event, context)

    try:
        # Validation
        print('# Request Validation Phase')
        print('## Check authorization header')

        authorization_header = EventHeadersJson.get_authorization_header(event)
        if authorization_header is None:
            return endpoint_response.forbidden()

        token_body = authorization_header.replace('TOKEN', '').strip()
        token_is_valid = shared_token_service.verify_token(token_body)
        if not token_is_valid:
            return endpoint_response.forbidden()

        # print('## Event body retrieval')
        # event_body_json = EventBodyJson.get_event_body_json(event)
        # if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

        print('## Query String Parameters')

        page_number = 1
        page_size = 5

        event_query_string_parameters_json = EventQueryStringParametersJson.get_event_query_string_parameters_json(
            event)
        if event_query_string_parameters_json.is_valid:
            print('event_query_string_parameters_json.is_valid')
            query_string_parameters = event_query_string_parameters_json.data_object
            page_number = int(query_string_parameters.get('page_number', 1))
            page_size = int(query_string_parameters.get('page_size', 5))

        # print('## Generating message from event body')
        # authenticate_user_credential_message = AuthenticateUserCredentialMessage.create_from_dict(event_body_json.data_object)
        # if authenticate_user_credential_message is None: return endpoint_response.bad_request('Invalid authenticate user credential message')

        # Repository action
        print('# Repository Action Phase')

        repository = RoleRepository()
        operation_result_message = repository.get_role_list()

        if operation_result_message.is_success:
            return endpoint_response.data(operation_result_message)
        return endpoint_response.bad_gateway(operation_result_message)
    except Exception as error:
        print(error)
        return endpoint_response.ok(False, f'HAS ERROR: {error}')



## Configuration

@endpoint_url('/ucm/configuration', 'GET')
def get_ucm_configuration(event:dict, context):
    """Get configuration
    Use case:
        (get configuration)
    """
    return dump_api_gateway_event_context(event, context)


## Notification

@endpoint_url('/ucm/notification', 'POST')
def post_ucm_notification(event:dict, context):
    """Post notification
    Use case:
        (post notification)
    """
    dump_api_gateway_event_context(event, context)

    event_body_json = EventBodyJson.get_event_body_json(event)
    if event_body_json.is_invalid: return endpoint_response.bad_request(event_body_json.error_message)

    chat_id = event_body_json.data_object.get("chatId", None)
    message = event_body_json.data_object.get("message", None)
    print("Sending message to chat_id:", chat_id, "with message:", message)

    notification = Notification()
    # notification.send_telegram_message('-1002841796915', 'hello world')
    send_success = notification.send_telegram_message(chat_id=chat_id, message=message)
    if send_success:
        return endpoint_response.ok(True, f'Message sent to chat {chat_id}')
    return endpoint_response.bad_request(f'Failed to send message to chat {chat_id}')

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
