'''SOME MODULE-LEVEL DOCS SPEC'''
import json
from os import environ
from datetime import datetime, timezone

import boto3

from utility_types import PasswordUtility


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

def __create_inventory_item_table():
    response = dynamodb_client.create_table(
        TableName='hci_inventory_item',
        AttributeDefinitions=[
            {'AttributeType': 'S', 'AttributeName': 'item_code'},
            {'AttributeType': 'S', 'AttributeName': 'item_description'},
        ],
        KeySchema=[
            {'AttributeName': 'item_code', 'KeyType': 'HASH'},
            {'AttributeName': 'item_description','KeyType': 'RANGE'},
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 1,'WriteCapacityUnits': 1}
    )
    print(response)

def __delete_table(table_name:str):
    response = dynamodb_client.delete_table(TableName=table_name)
    print(response)

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

def put_inventory_item(item_code: str, item_description:str):
    response = dynamodb_client.put_item(
        TableName=INVENTORY_ITEM_TABLE_NAME,
        Item={
            'item_code':  {'S': item_code},
            'item_description':  {'S': item_description},
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
        ReturnConsumedCapacity='TOTAL'
    )
    print(response)


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
    if 'item_code' not in json: return None
    return NewInventoryItemMessage(json['item_code'])

def add_item(event:dict, context):
    if 'body' not in event:
        return response(HTTP_BAD_REQUEST_CODE, '`body` not found in context')

    request_json = json.loads(event['body'])
    new_inventory_item_message = __create_new_inventory_item_message(request_json)

    if new_inventory_item_message is None: return response(HTTP_BAD_REQUEST_CODE,
                                               json.dumps(OperationResult(False, 'Invalid new inventory item message')))

    # TODO: Add item to data store

    return response(HTTP_OK_CODE, json.dumps(OperationResult(True)))



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
    if 'user_code' not in json: return None
    if 'item_code' not in json: return None
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

# def dump_event_context(event, context):
#     ''' Read an item by ID.
#     Args:
#         item_id (int): The ID of the item to retrieve.
#         q (str, optional): An optional query parameter.
#     Returns:
#         dict: A dictionary containing the item details.
#     '''
    
#     print("[event]")
#     print(event)
#     print("[context]")
#     print(context)
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Return from Lambda 2')
#     }

#

class SGID(object):
    """
    SGID is a 9 character long string
    # 123456789
    # @1234567C
    # Letter "S", "T", "F", "G" or "M"
    # 7-digit
    # Checksum
    """
    def __init__(self, raw_string):
        self.raw_data = raw_string

    def has_valid_status_char(self):
        valid_status_character_list = [
             'S' # Singapore citizens and permanent residents born before 1 January 2000
            ,'T' # Singapore citizens and permanent residents born on or after 1 January 2000
            ,'F' # Foreigners issued with long-term passes before 1 January 2000
            ,'G' # Foreigners issued with long-term passes from 1 January 2000 to 31 December 2021
            ,'M' # Foreigners issued with long-term passes on or after 1 January 2022
        ]
        return self.raw_data[0] in valid_status_character_list

    def has_valid_checksum_char(self):
        """
        The steps involved in the computation are as follows:

        Multiply each digit in the NRIC number by its weight i.e. 2 7 6 5 4 3 2 in order.
        Add together the above products.
        If the first letter i.e. UIN of the NRIC starts with T or G, add 4 to the total.
        Find the remainder of (sum calculated above) mod 11.
        If the NRIC starts with F or G: 0=X, 1=W, 2=U, 3=T, 4=R, 5=Q, 6=P, 7=N, 8=M, 9=L, 10=K
        If the NRIC starts with S or T: 0=J, 1=Z, 2=I, 3=H, 4=G, 5=F, 6=E, 7=D, 8=C, 9=B, 10=A
        """
        #          1  2  3  4  5  6  7
        weights = [2, 7, 6, 5, 4, 3, 2]
        #               0    1    2    3    4    5    6    7    8    9   10
        sgp_map     = ['J', 'Z', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
        non_sgp_map = ['X', 'W', 'U', 'T', 'R', 'Q', 'P', 'N', 'M', 'L', 'K']
        post_2000_char_list = ['T', 'G']

        issue_char = self.raw_data[0]
        sum_of_checks = 0

        for index, number in enumerate(list(self.raw_data[1:8])): sum_of_checks = sum_of_checks + (weights[index] * int(number))

        if issue_char in post_2000_char_list:
            sum_of_checks = sum_of_checks + 4

        checksum_modulus = sum_of_checks % 11

        sgp_char_list = ['S', 'T']

        return self.raw_data[8] == sgp_map[checksum_modulus] if issue_char in sgp_char_list else non_sgp_map[checksum_modulus]

    def is_valid(self):
        if len(self.raw_data) != 9:
            return False
        if not self.has_valid_status_char():
            return False
        if not self.has_valid_checksum_char():
            return False


if __name__ == "__main__":
    pass
    sgid = SGID('S7940180C')
    is_valid = sgid.has_valid_checksum_char()
    print('is_valid', is_valid)
    # sum_of_checks = 0
    # a = 'S7940180C'
    # weights = [2, 7, 6, 5, 4, 3, 2]
    # for index, number in enumerate(list(a[1:8])):
    #     print(weights[index], number)
    #     sum_of_checks = sum_of_checks + (weights[index] * int(number))
    #
    #
    # post_2000_char_list = ['T', 'G']
    # if a[0] in post_2000_char_list:
    #     sum_of_checks = sum_of_checks + 4
    #
    # checksum_modulus = sum_of_checks % 11
    #
    # sgp_char_list = ['S', 'T']
    # sgp_map = ['J', 'Z', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
    # non_sgp_map = ['X', 'W', 'U', 'T', 'R', 'Q', 'P', 'N', 'M', 'L', 'K']
    # if a[0] in sgp_char_list:
    #     print('sum_of_checks', sgp_map[checksum_modulus])
    # else:
    #     print('sum_of_checks', non_sgp_map[checksum_modulus])


    #print( enumerate(list(a[1:8])) )
    #num_list = list(map(lambda x,y: print(x, y) , list(a[1:8])))
    #num_list = list(map(lambda i, x: {'name': x, 'rank': i}, enumerate(list(a[1:8]))))
    #print(num_list)

    # id = SGID('S7940180C')
    # #is_valid = id.is_valid()
    # is_valid = id.has_valid_checksum_char()
    # print('is valid id', is_valid)

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

    # CREATE/DELETE TABLE
    #__delete_table('inventory_item')
    #__create_inventory_item_table()

    # ADD INVENTORY ITEM
    #put_inventory_item('code1', 'ITEM 1')
    #put_inventory_item('code2', 'ITEM 2')
    #put_inventory_item('code3', 'ITEM 3')

    #print(result)
#     import sys
#     if len(sys.argv) < 2: 
#         print(sys.argv)
#         print (len(sys.argv))
#         raise Exception('Too little arguments')
#     print(globals()[sys.argv[1]].__doc__)