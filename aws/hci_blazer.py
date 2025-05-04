'''SOME MODULE-LEVEL DOCS SPEC'''
import json
from os import environ
from datetime import datetime, timezone, timedelta

import boto3
import botocore.exceptions

from utility_types import PasswordUtility
from hci_decorators import endpoint_url, dump_api_gateway_event_context

import pdb


# GENERAL HTTP-RELATED STUFF

HTTP_OK_CODE = 200
HTTP_BAD_REQUEST_CODE = 400

def response(http_code:int, body_text:str):
    return {
        'statusCode': http_code,
        'body': json.dumps(body_text)
    }


# AWS PROFILE SETUP

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
boto3.setup_default_session(profile_name=aws_profile)


# AWS Setup DynamoDB

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

def __list_tables():
    response = dynamodb_client.list_tables()
    return response


# AWS DynamoDb generic helper function

def get_record_value(item:dict):
    for item_key in item.keys():
        match item_key:
            case 'S': return item[item_key]
            case 'N': return float(item[item_key])
            case 'NULL': return None if item[item_key] == True else False
            case _: return item[item_key]
    return None


USER_CREDENTIAL_TABLE_NAME = 'user_credential'

def get_user_credential_list():
    response = dynamodb_client.scan(TableName=USER_CREDENTIAL_TABLE_NAME)
    record_list = response['Items']
    result_list = []
    for record in record_list:
        newObject = {}
        for record_key in sorted(record.keys(), key=lambda x:x.lower()):
            newObject[record_key] = get_record_value(record[record_key])
        result_list.append(newObject)
    return result_list

def get_user_credential(username:str) -> dict:
    response = dynamodb_client.get_item(
        TableName=USER_CREDENTIAL_TABLE_NAME,
        Key={
            'username': {'S': username}
        }
    )
    if 'Item' not in response:
        return None

    record = response['Item']
    newObject = {}
    for record_key in sorted(record.keys(), key=lambda x:x.lower()):
        newObject[record_key] = get_record_value(record[record_key])
    return newObject

def put_user_credential(username: str, password_text: str):
    pwd_util = PasswordUtility()
    (hex_digest, salt_b64) = pwd_util.hash_password(password_text, None)

    response = dynamodb_client.put_item(
        TableName=USER_CREDENTIAL_TABLE_NAME,
        Item={
            'failed_login_attempts': {'N': '0'},
            'last_login_attempt_datetime': {'NULL': True},
            'last_successful_login': {'NULL': True},
            'password_hash': {'S': hex_digest},
            'password_last_changed_datetime': {'S': datetime.now(timezone.utc).isoformat()},
            'password_salt': {'S': salt_b64},
            'status': {'S': 'NEW',},
            'username': {'S': f'hci-{username}'},
        },
        ReturnConsumedCapacity='TOTAL'
    )
    print(response)


INVENTORY_ITEM_TABLE_NAME = 'hci_inventory_item'

def put_inventory_item(item_code: str) -> bool:
    try:
        response = dynamodb_client.put_item(
            TableName=INVENTORY_ITEM_TABLE_NAME,
            Item={
                'item_code':  {'S': item_code},
                'item_description': {'S': item_code},
                'borrower_code': {'NULL': True},
                'borrow_datetime': {'NULL': True},
                'target_return_datetime': {'NULL': True},
                # 'last_borrow_datetime': {'NULL': True},
                # 'last_changed_datetime': {'S': datetime.now(timezone.utc).isoformat()},
                # 'failed_login_attempts': {'N': '0'},
                # 'last_login_attempt_datetime': {'NULL': True},
                # 'last_successful_login': {'NULL': True},
                # 'password_hash': {'S': hex_digest},
                # 'username': {'S': f'hci-{username}'},
            },
            ConditionExpression = "attribute_not_exists(item_code)",
            ReturnConsumedCapacity='TOTAL'
        )
        print(response)
        return True
    except botocore.exceptions.ClientError as e:
        print(e)
        return False
        # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        #     print('This was not a unique key')
        # else:
        #     print('some other dynamodb related error')

def __get_field_value(value):
    value_tuple = value.popitem()  # value tuple consists of a type-value like: { 'S': 'SomeValue' }
    if value_tuple[0] == 'NULL':
        return None
    if value_tuple[0] == 'N':
        return float(value_tuple[1])
    if value_tuple[0] == 'S':
        return value_tuple[1]
    return value_tuple[1]

def __map_to_inventory_item(item:any):
    newObject = {}
    for key, value in sorted(item.items()):
        newObject[key] = __get_field_value(value)
    return newObject

def get_all_inventory_item_list(event:dict, context):
    result_list = []
    for response in dynamodb_client.get_paginator('scan').paginate(TableName=INVENTORY_ITEM_TABLE_NAME):
        if 'Items' in response:
            result_list.extend(list(map(__map_to_inventory_item, response['Items'])))
    result_list.sort(key=lambda record: record['item_description'])
    return result_list

def delete_inventory_item_table():
    response = dynamodb_client.delete_table(TableName=INVENTORY_ITEM_TABLE_NAME)
    print(response)

def create_inventory_item_table():
    response = dynamodb_client.create_table(
        TableName=INVENTORY_ITEM_TABLE_NAME,
        KeySchema=[
            { 'AttributeName': 'item_code', 'KeyType': 'HASH'}
            #{ 'AttributeName': 'SongTitle', 'KeyType': 'RANGE',},
        ],

        AttributeDefinitions=[
            {'AttributeName': 'item_code', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )
    print(response)

def borrow_inventory_item(item_code:str, user_code:str):
    timestamp = datetime.now(timezone.utc)
    borrow_duration = timedelta(days=14)
    try:
        response = dynamodb_client.update_item(
            TableName=INVENTORY_ITEM_TABLE_NAME,
            Key={
                'item_code': {'S': item_code}
            },
            UpdateExpression='SET #BORROW_DATETIME = :borrow_datetime, #BORROWER_CODE = :borrower_code, #TARGET_RETURN_DATETIME = :target_return_datetime',
            ExpressionAttributeNames={
                '#BORROW_DATETIME': 'borrow_datetime',
                '#BORROWER_CODE': 'borrower_code',
                '#TARGET_RETURN_DATETIME': 'target_return_datetime'
            },
            ExpressionAttributeValues={
                ':borrow_datetime'          : {'S': timestamp.isoformat() },
                ':borrower_code'            : {'S': user_code},
                ':target_return_datetime'   : {'S': (timestamp + borrow_duration).isoformat(), },
                ':v_sub'                    : {'S': 'NULL', }
            },
            ConditionExpression="attribute_type(borrower_code, :v_sub)",
            ReturnValues='ALL_NEW',
        )
        print(response)
        return True
    except botocore.exceptions.ClientError as e:
        print(e)
        error_code = e.response['Error']['Code'] # 'ConditionalCheckFailedException'
        return False
        # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        #     print('This was not a unique key')
        # else:
        #     print('some other dynamodb related error')

def return_inventory_item(item_code:str):
    timestamp = datetime.now(timezone.utc)
    borrow_duration = timedelta(days=14)
    try:
        response = dynamodb_client.update_item(
            TableName=INVENTORY_ITEM_TABLE_NAME,
            Key={
                'item_code': {'S': item_code}
            },
            UpdateExpression='SET #BORROW_DATETIME = :borrow_datetime, #BORROWER_CODE = :borrower_code, #TARGET_RETURN_DATETIME = :target_return_datetime',
            ExpressionAttributeNames={
                '#BORROW_DATETIME': 'borrow_datetime',
                '#BORROWER_CODE': 'borrower_code',
                '#TARGET_RETURN_DATETIME': 'target_return_datetime'
            },
            ExpressionAttributeValues={
                ':borrow_datetime'          : {'NULL': True },
                ':borrower_code'            : {'NULL': True },
                ':target_return_datetime'   : {'NULL': True },
                ':v_sub'                    : {'S': 'NULL'},
            },
            ConditionExpression="NOT attribute_type(borrower_code, :v_sub)",
            ReturnValues='ALL_NEW',
        )
        print(response)
        return True
    except botocore.exceptions.ClientError as e:
        print(e)
        error_code = e.response['Error']['Code'] # 'ConditionalCheckFailedException'
        return False
        # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        #     print('This was not a unique key')
        # else:
        #     print('some other dynamodb related error')


# OBSOLETE
def xxxget_inventory_item_page_list(page_number:int, page_size:int=3):
    offset_to_start_reading = (page_number - 1) * page_size
    print(f"offset_to_start_reading: {offset_to_start_reading}")
    read_count = 0
    result_list = []
    for response in dynamodb_client.get_paginator('scan').paginate(TableName=INVENTORY_ITEM_TABLE_NAME, PaginationConfig={'PageSize': 3}):
        if 'Items' not in response:
            continue
        print(f"read_count: {read_count}, offset_to_start_reading: {offset_to_start_reading}")
        if read_count >= offset_to_start_reading:
            result_list.extend(list(map(__map_to_inventory_item, response['Items'])))
        read_count = read_count + len(response['Items'])
        if len(result_list) >= page_size:
            pass
    return result_list

def xxxget_all_inventory_item_list():
    result_list = []
    response = dynamodb_client.scan(TableName=INVENTORY_ITEM_TABLE_NAME, Limit=3)
    if 'Items' in response:
        result_list.extend(list(map(__map_to_inventory_item, response['Items'])))
    while 'LastEvaluatedKey' in response:
        last_evaluated_key = response['LastEvaluatedKey']
        response = dynamodb_client.scan(TableName=INVENTORY_ITEM_TABLE_NAME, Limit=3, ExclusiveStartKey = last_evaluated_key)
        if 'Items' in response:
            result_list.extend(list(map(__map_to_inventory_item, response['Items'])))

    return result_list
    # if 'Items' in response:
    #     return (response['Items'], lastEvaluatedKey)
    # if exclusiveStartKey is None:
    #     response = dynamodb_client.scan(
    #         TableName=INVENTORY_ITEM_TABLE_NAME,
    #         Limit=page_size
    #     )
    # else:
    #     response = dynamodb_client.scan(
    #         TableName=INVENTORY_ITEM_TABLE_NAME,
    #         Limit=page_size,
    #         ExclusiveStartKey=exclusiveStartKey
    #     )
    #print(response)
    # lastEvaluatedKey = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None


# def get_inventory_item_list(page_size:int, page_number:int, exclusiveStartKey:dict|None = None):
#     if exclusiveStartKey is None:
#         response = dynamodb_client.scan(
#             TableName=INVENTORY_ITEM_TABLE_NAME,
#             Limit=page_size
#         )
#     else:
#         response = dynamodb_client.scan(
#             TableName=INVENTORY_ITEM_TABLE_NAME,
#             Limit=page_size,
#             ExclusiveStartKey=exclusiveStartKey
#         )
#
#     #print(response)
#     lastEvaluatedKey = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None
#     if 'Items' in response:
#         return (response['Items'], lastEvaluatedKey)

# GENERIC ENTITIES

class Message(object):
    pass


# USER-AUTHENTICATION RELATED STUFF

class CredentialMessage(Message):
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
    def __str__(self):
        return f"username:{self.username}, password:{'None' if self.password == None else '****'}"

def __create_credential_message(json:dict) -> CredentialMessage|None:
    if 'username' not in json: return None
    if 'password' not in json: return None
    return CredentialMessage(json['username'], json['password'])

def __validate_user_credential(credential_message:CredentialMessage, user_credential) -> bool:
    pwd_util = PasswordUtility()
    salt_str = user_credential['password_salt']
    salt_bytes = pwd_util.decode_base64_to_bytes(salt_str)
    (sha256_hex, salt_b64) = pwd_util.hash_password(credential_message.password, salt_bytes)
    return user_credential['password_hash'] == sha256_hex

def __get_user_credential(credential_message:CredentialMessage) -> dict:
    user_credential = get_user_credential(credential_message.username)
    result = {
        'is_valid' : user_credential is not None
    }
    #return user_credential or {} | result
    return user_credential

def authenticate_user_credential(event:dict, context):
    """
    Authenticate user credentials (body)
    Returns:
        dict:
            A dictionary for an authentication ticket. Dictionary will have the following fields:
            1. is_valid:bool (required)
            1. username:str (optional)
    """
    print("[event]", event)
    print("[context]", context)

    if 'body' not in event:
        return response(HTTP_BAD_REQUEST_CODE, '`body` not found in context')

    request_json = json.loads(event['body'])

    credential_message = __create_credential_message(request_json)
    if credential_message is None: return response(HTTP_BAD_REQUEST_CODE, 'Invalid credential message')

    user_credential = __get_user_credential(credential_message)

    # If user credential is not found, then naturally is invalid log in
    if user_credential is None:
        return {
            'is_valid': False
        }

    # Logic to verify if credentials matches what was stored in database
    is_valid_user_credential = __validate_user_credential(credential_message, user_credential)
    if is_valid_user_credential == False:
        return {
            'is_valid': False
        }

    return {
        'is_valid': True,
        'username': user_credential['username']
    }

    #
    #


    # if user_credential is None:
    #     return response(HTTP_OK_CODE, json.dumps({

    #     }))

    # if credentials_are_valid(json):
    #     authentication_ticket = {
    #         'username': 'zhixian@hotmail.com',
    #         'credentials_are_authentic' : True,
    #         'checksum' : '##!!()*!)*'
    #     }
    #     return response(HTTP_OK_CODE, json.dumps(authentication_ticket))
    # else:
    #     return response(HTTP_OK_CODE, json.dumps(authentication_ticket))



    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('authenticate_user_credential')
    # }

# INVENTORY RELATED STUFF

class NewInventoryItemMessage(Message):
    def __init__(self, item_code:str):
        self.item_code = item_code
    def __str__(self):
        return f"Item code:{self.item_code}"

def __create_new_inventory_item_message(json:dict) -> NewInventoryItemMessage|None:
    if 'itemCode' not in json: return None
    return NewInventoryItemMessage(json['itemCode'])

def add_item(event:dict, context):
    if 'body' not in event:
        return response(HTTP_BAD_REQUEST_CODE, '`body` not found in context')

    request_json = json.loads(event['body'])
    new_inventory_item_message = __create_new_inventory_item_message(request_json)

    if new_inventory_item_message is None: return response(HTTP_BAD_REQUEST_CODE,
                                               json.dumps(OperationResult(False, 'Invalid new inventory item message').__dict__))

    is_success = put_inventory_item(new_inventory_item_message.item_code)

    # ERROR HANDLING?

    #return response(HTTP_OK_CODE, json.dumps(OperationResult(True).__dict__))
    return_message = f'{new_inventory_item_message.item_code} added successfully' if is_success else f'{new_inventory_item_message.item_code} fail to add'
    return {
        'statusCode': HTTP_OK_CODE,
        'body': json.dumps(OperationResult(is_success, return_message).__dict__)
    }

class GetInventoryItemListMessage(Message):
    def __init__(self, page_size:int, page_number:int):
        self.page_size = page_size
        self.page_number = page_number
    def __str__(self):
        return f"Item code:{self.item_code}"

def __create_get_inventory_item_list_message(json:dict) -> GetInventoryItemListMessage|None:
    if 'pageSize' not in json: return None
    if 'pageNumber' not in json: return None
    return GetInventoryItemListMessage(json['pageSize'], json['pageNumber'])

def get_item_list(event:dict, context):
    if 'body' not in event:
        return response(HTTP_BAD_REQUEST_CODE, '`body` not found in context')

    request_json = json.loads(event['body'])
    get_inventory_item_list_message = __create_get_inventory_item_list_message(request_json)

    if get_inventory_item_list_message is None: return response(HTTP_BAD_REQUEST_CODE,
                                               json.dumps(OperationResult(False, 'Invalid get_inventory_item_list message').__dict__))

    #item_list = get_all_inventory_item_list(get_inventory_item_list_message.page_size, get_inventory_item_list_message.page_number)
    item_list = get_all_inventory_item_list()

    # ERROR HANDLING?

    #return response(HTTP_OK_CODE, json.dumps(OperationResult(True).__dict__))
    #return_message = f'{new_inventory_item_message.item_code} added successfully' if is_success else f'{new_inventory_item_message.item_code} fail to add'
    return {
        'statusCode': HTTP_OK_CODE,
        'body': json.dumps(item_list)
    }


# BORROW RELATED STUFF

class OperationResult(Message):
    def __init__(self, operation_is_successful:bool, message:str|None = None):
        self.success = operation_is_successful
        self.message = message
    def __str__(self):
        return f"Operation is successful:{self.success}, Message:{self.message}"

class BorrowMessage(Message):
    def __init__(self, user_code:str, item_code:str):
        self.user_code = user_code
        self.item_code = item_code
    def __str__(self):
        return f"User code:{self.user_code}, Item code:{self.item_code}"

def __create_borrow_message(json:dict) -> BorrowMessage|None:
    if 'userCode' not in json: return None
    if 'itemCode' not in json: return None
    return BorrowMessage(json['user_code'], json['item_code'])

# ??
def validate_borrower_id(event:dict, context):
    print("[event]", event)
    print("[context]", context)

    if 'body' not in event:
        return response(HTTP_BAD_REQUEST_CODE, '`body` not found in context')

    request_json = json.loads(event['body'])
    # credential_message = __create_credential_message(request_json)
    # if credential_message is None: return response(HTTP_BAD_REQUEST_CODE, 'Invalid credential message')
    # TODO: Checks if requests contains a valid borrower ID
    is_valid = False

    return {
        'is_valid': is_valid
    }

# ??
def validate_item_id(event:dict, context):
    print("[event]", event)
    print("[context]", context)

    if 'body' not in event:
        return response(HTTP_BAD_REQUEST_CODE, '`body` not found in context')

    request_json = json.loads(event['body'])
    # credential_message = __create_credential_message(request_json)
    # if credential_message is None: return response(HTTP_BAD_REQUEST_CODE, 'Invalid credential message')
    # TODO: Checks if requests contains a valid item ID
    is_valid = False

    return {
        'is_valid': is_valid
    }


def failed_operation_result(message:str):
    operation_result = {
        'is_success': False,
        'message': message
    }
    return operation_result


def has_valid_user_code(borrow_message:BorrowMessage) -> bool:
    return True

def has_valid_item_code(borrow_message:BorrowMessage) -> bool:
    return True

def confirm_borrow(event:dict, context):
    if 'body' not in event:
        return response(HTTP_BAD_REQUEST_CODE, '`body` not found in context')

    request_json = json.loads(event['body'])
    borrow_message = __create_borrow_message(request_json)

    if borrow_message is None: return response(HTTP_BAD_REQUEST_CODE, json.dumps(OperationResult(False, 'Invalid borrow message')))

    if not has_valid_user_code(borrow_message):
        return response(HTTP_OK_CODE, json.dumps(OperationResult(False, 'Invalid user code')))
    if not has_valid_item_code(borrow_message):
        return response(HTTP_OK_CODE, json.dumps(OperationResult(False, 'Invalid item code')))

    # TODO: Update record in data

    return response(HTTP_OK_CODE, json.dumps(OperationResult(True)))


# END-POINTS




@endpoint_url('/hci-blazer/auth', 'POST')
def post_hci_blazer_auth(event:dict, context):
    dump_api_gateway_event_context(event, context)

@endpoint_url('/hci-blazer/item', 'GET')
def get_hci_blazer_item(event:dict, context):
    dump_api_gateway_event_context(event, context)

@endpoint_url('/hci-blazer/item', 'POST')
def post_hci_blazer_item(event:dict, context):
    dump_api_gateway_event_context(event, context)

@endpoint_url('/hci-blazer/item', 'PATCH')
def patch_hci_blazer_item(event:dict, context):
    dump_api_gateway_event_context(event, context)

@endpoint_url('/hci-blazer/item', 'DELETE')
def delete_hci_blazer_item(event:dict, context):
    dump_api_gateway_event_context(event, context)

@endpoint_url('/hci-blazer/item/{id}', 'GET')
def patch_hci_blazer_item_id(event:dict, context):
    dump_api_gateway_event_context(event, context)


if __name__ == "__main__":
    pass
    get_hci_blazer_item()
    # CREATE CREDENTIAL
    #result = put_user_credential('zhixian', 'pass1234')
    #print(result)
    # VIEW CREDENTIAL
    # credential_message = CredentialMessage('hci-zhixian1', 'adasd')
    # result = __get_user_credential(credential_message)
    # print(result)
    # VALIDATE CREDENTIAL
    # LIST TABLES
    # response = __list_tables()
    # table_name_list = response['TableNames']
    # print(table_name_list)
    # print("Table count:", len(table_name_list))
    # import pdb
    # target_page = 3
    # last_key = None
    # current_page = 0
    # while current_page < target_page:
    #     (item_list, last_key) = get_inventory_item_list(8, current_page, last_key)
    #     current_page = current_page + 1
    #     print("Run iteration page", current_page, len(item_list))
    #     if last_key is None:
    #         break
    # item_list = get_all_inventory_item_list()
    # print('item_list', item_list)
    # result = get_all_inventory_item_list()

    # result = get_all_inventory_item_list()
    # print(result)

    #delete_inventory_item_table()
    #create_inventory_item_table()
    #put_inventory_item('item 1')
    # borrow_inventory_item('item 1', 'test user')
    # return_inventory_item('item 1')

#     import sys
#     if len(sys.argv) < 2: 
#         print(sys.argv)
#         print (len(sys.argv))
#         raise Exception('Too little arguments')
#     print(globals()[sys.argv[1]].__doc__)