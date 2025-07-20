"""
Sections:
    AWS Setup
    Entity classes
        UserCredentialEntity
        AddUserCredentialEntity
    Repository classes
        UserCredentialRepository
"""
import json
import logging
from datetime import datetime
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

import boto3
from botocore.exceptions import ClientError

from utility_types import PasswordUtility
from shared_data_repositories import DynamoDbEntity, BaseRepository
from shared_messages import OperationResultMessage
from shared_user_credential_messages import AddUserCredentialMessage, AuthenticateUserCredentialMessage, UpdateUserCredentialPasswordMessage

import pdb

# AWS SETUP

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
if runtime_dns_domain == 'AD.MLP.COM': reset_tzpath(['C:/Anaconda3/share/zoneinfo'])

boto3.setup_default_session(profile_name=aws_profile)

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")


# ENTITY CLASSES

## RULE ENTITY CLASSES

class UserCredentialEntity(DynamoDbEntity):
    """Base Configuration entity class.
    A user credential record can have the following fields:
    1. username
    1. failed_login_attempts
    1. last_login_attempt_datetime
    1. last_successful_login

    1. password_hash
    1. password_last_changed_datetime
    1. password_salt
    1. status

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """

    USERNAME_FIELD_NAME = 'username'
    FAILED_LOGIN_ATTEMPTS_FIELD_NAME = 'failed_login_attempts'
    LAST_LOGIN_ATTEMPT_DATETIME_FIELD_NAME = 'last_login_attempt_datetime'
    LAST_SUCCESSFUL_LOGIN_FIELD_NAME = 'last_successful_login'

    PASSWORD_HASH_FIELD_NAME = 'password_hash'
    PASSWORD_LAST_CHANGED_DATETIME_FIELD_NAME = 'password_last_changed_datetime'
    PASSWORD_SALT_FIELD_NAME = 'password_salt'
    STATUS_FIELD_NAME = 'status'
    ROLES_FIELD_NAME = 'roles'

    RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
    RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
    RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'

    private_fields = [
        'last_login_attempt_datetime',
        'last_successful_login',
        'password_hash',
        'password_salt',
        'record_update_by',
        'record_update_datetime',
        'record_create_by',
        'record_create_datetime']

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.username = None
        self.failed_login_attempts = None
        self.last_login_attempt_datetime = None
        self.last_successful_login = None

        self.password_hash = None
        self.password_last_changed_datetime = None
        self.password_salt = None
        self.status = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None
        self.roles = []

        if len(args) > 0 and isinstance(args[0], dict):
            self.load_from_dict(args[0])

    def to_dynamodb_item(self):
        item = {
            'username': self.dynamodb_null_value() if self.username is None else self.dynamodb_string_value(self.username),
            'failed_login_attempts': self.dynamodb_null_value() if self.failed_login_attempts is None else self.dynamodb_number_value(self.failed_login_attempts),
            'last_login_attempt_datetime': self.dynamodb_null_value() if self.last_login_attempt_datetime is None else self.dynamodb_string_value(self.last_login_attempt_datetime.isoformat()),
            'last_successful_login': self.dynamodb_null_value() if self.last_successful_login is None else self.dynamodb_string_value(self.last_successful_login),

            'password_hash': self.dynamodb_null_value() if self.password_hash is None else self.dynamodb_string_value(self.password_hash),
            'password_last_changed_datetime': self.dynamodb_null_value() if self.password_last_changed_datetime is None else self.dynamodb_string_value(self.password_last_changed_datetime.isoformat()),
            'password_salt': self.dynamodb_null_value() if self.password_salt is None else self.dynamodb_string_value(self.password_salt),
            'status': self.dynamodb_null_value() if self.status is None else self.dynamodb_string_value(self.status),
            'roles': self.dynamodb_null_value() if len(self.roles) <= 0 else self.dynamodb_string_set_value(self.roles),

            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

    def load_from_dict(self, data:dict):
        self.username = self.map_from_dynamodb_attribute(data, UserCredentialEntity.USERNAME_FIELD_NAME)
        self.failed_login_attempts = self.map_from_dynamodb_attribute(data, UserCredentialEntity.FAILED_LOGIN_ATTEMPTS_FIELD_NAME)
        self.last_login_attempt_datetime = self.map_from_dynamodb_attribute(data, UserCredentialEntity.LAST_LOGIN_ATTEMPT_DATETIME_FIELD_NAME)
        self.last_successful_login = self.map_from_dynamodb_attribute(data, UserCredentialEntity.LAST_SUCCESSFUL_LOGIN_FIELD_NAME)

        self.password_hash = self.map_from_dynamodb_attribute(data, UserCredentialEntity.PASSWORD_HASH_FIELD_NAME)
        self.password_last_changed_datetime = self.map_from_dynamodb_attribute(data, UserCredentialEntity.PASSWORD_LAST_CHANGED_DATETIME_FIELD_NAME)
        self.password_salt = self.map_from_dynamodb_attribute(data, UserCredentialEntity.PASSWORD_SALT_FIELD_NAME)
        self.status = self.map_from_dynamodb_attribute(data, UserCredentialEntity.STATUS_FIELD_NAME)
        self.roles = self.map_from_dynamodb_attribute(data, UserCredentialEntity.ROLES_FIELD_NAME)

        self.record_update_by = self.map_from_dynamodb_attribute(data, UserCredentialEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_update_datetime = self.map_from_dynamodb_attribute(data, UserCredentialEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_create_by = self.map_from_dynamodb_attribute(data, UserCredentialEntity.RECORD_CREATE_BY_FIELD_NAME)
        self.record_create_datetime = self.map_from_dynamodb_attribute(data, UserCredentialEntity.RECORD_CREATE_DATETIME_FIELD_NAME)

    def __str__(self):
        """human-readable, informal string representation"""
        return (f"{UserCredentialEntity.USERNAME_FIELD_NAME}: {self.username}, "
                f"{UserCredentialEntity.STATUS_FIELD_NAME}: {self.status}")

    # def __repr__(self):
    #     """unambiguous, developer-friendly string representation"""
    #     return json.dumps(self.__dict__)

    def to_json_object(self, public_only=False):
        if public_only:
            for field_name in UserCredentialEntity.private_fields:
                self.__dict__.pop(field_name)

        return self.__dict__

    @staticmethod
    def get_record_timestamp() -> datetime:
        # record_timestamp = datetime.now(timezone.utc).as timezone(SINGAPORE_TIMEZONE)
        record_timestamp = datetime.now(SINGAPORE_TIMEZONE)
        return record_timestamp

class AddUserCredentialEntity(UserCredentialEntity):
    """(Re)place or In(sert) a configuration record."""
    def __init__(self, add_user_credential_message:AddUserCredentialMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.username = add_user_credential_message.username

        self.failed_login_attempts = '0'
        self.last_login_attempt_datetime = None
        self.last_successful_login = None

        password_utility = PasswordUtility()
        (sha256_hex, salt_b64) = password_utility.hash_password(password_text=add_user_credential_message.password)
        self.password_hash = sha256_hex
        self.password_last_changed_datetime = record_timestamp
        self.password_salt = salt_b64
        self.status = 'NEW'

        self.record_update_by = 'NOT SET'
        self.record_update_datetime = record_timestamp
        self.record_create_by = 'NOT SET'
        self.record_create_datetime = record_timestamp

class SuccessfulLoginUserCredentialUpdateEntity(UserCredentialEntity):
    """On successful login, update
    self.failed_login_attempts =
    self.last_login_attempt_datetime
    self.last_successful_login
    self.record_update_datetime
    """
    def __init__(self, username:str):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.username = username                                # KEY
        self.failed_login_attempts = '0'                        # UPDATE
        self.last_login_attempt_datetime = record_timestamp     # UPDATE
        self.last_successful_login = record_timestamp           # UPDATE
        self.record_update_by = 'NOT SET'                       # UPDATE
        self.record_update_datetime = record_timestamp          # UPDATE

    # Components of update

    def update_item_key(self):
        return {
            'username': {'S': self.username}
        }

    def update_item_update_expression(self) -> str:
        return ('SET #FAILED_LOGIN_ATTEMPTS = :failed_login_attempts, '
                '#LAST_LOGIN_ATTEMPT_DATETIME = :last_login_attempt_datetime, '
                '#LAST_SUCCESSFUL_LOGIN = :last_successful_login, '
                '#RECORD_UPDATE_BY = :record_update_by, '
                '#RECORD_UPDATE_DATETIME = :record_update_datetime')

    def update_item_get_expression_attribute_names(self):
        return {
            '#FAILED_LOGIN_ATTEMPTS'        : 'failed_login_attempts',
            '#LAST_LOGIN_ATTEMPT_DATETIME'  : 'last_login_attempt_datetime',
            '#LAST_SUCCESSFUL_LOGIN'        : 'last_successful_login',
            '#RECORD_UPDATE_BY'             : 'record_update_by',
            '#RECORD_UPDATE_DATETIME'       : 'record_update_datetime',
        }

    def update_item_expression_attribute_values(self):
        return {
            ':failed_login_attempts'        : self.dynamodb_number_value(self.failed_login_attempts),
            ':last_login_attempt_datetime'  : self.dynamodb_string_value(self.last_login_attempt_datetime.isoformat()),
            ':last_successful_login'        : self.dynamodb_string_value(self.last_successful_login.isoformat()),
            ':record_update_by'             : self.dynamodb_string_value(self.record_update_by),
            ':record_update_datetime'       : self.dynamodb_string_value(self.record_update_datetime.isoformat())
        }

    def update_item_conditional_expression(self):
        return "attribute_exists(username)"

class FailedLoginUserCredentialUpdateEntity(UserCredentialEntity):
    """On failed login, update
    self.failed_login_attempts =
    self.last_login_attempt_datetime
    self.record_update_datetime
    """
    def __init__(self, username:str):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.username = username                                # KEY
        self.failed_login_attempts = '0'                        # UPDATE
        self.last_login_attempt_datetime = record_timestamp     # UPDATE
        self.record_update_by = 'NOT SET'                       # UPDATE
        self.record_update_datetime = record_timestamp          # UPDATE

    # Components of update

    def __update_expression(self):
        return ('ADD #FAILED_LOGIN_ATTEMPTS :incr_value '
                'SET #LAST_LOGIN_ATTEMPT_DATETIME = :last_login_attempt_datetime, '
                '#RECORD_UPDATE_BY = :record_update_by, '
                '#RECORD_UPDATE_DATETIME = :record_update_datetime')

    def __update_expression_attribute_names(self):
        return {
            '#FAILED_LOGIN_ATTEMPTS': 'failed_login_attempts',
            '#LAST_LOGIN_ATTEMPT_DATETIME': 'last_login_attempt_datetime',
            '#RECORD_UPDATE_BY': 'record_update_by',
            '#RECORD_UPDATE_DATETIME': 'record_update_datetime',
        }

    def __update_expression_attribute_values(self):
        return {
            ':incr_value': self.dynamodb_number_value('1'),
            ':last_login_attempt_datetime': self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            ':record_update_by': self.dynamodb_string_value(self.record_update_by),
            ':record_update_datetime': self.dynamodb_string_value(self.record_update_datetime.isoformat())
        }


    def update_transact_item(self, table_name:str):
        return {
            'Update': {
                'TableName': table_name,
                'Key': {'username': {'S': self.username}},
                'UpdateExpression': self.__update_expression(),
                'ExpressionAttributeNames': self.__update_expression_attribute_names(),
                'ExpressionAttributeValues': self.__update_expression_attribute_values(),
                'ConditionExpression': 'attribute_exists(username)'
            }
        }

    def to_transact_items(self, table_name:str):
        transact_items = []
        transact_items.append(self.update_transact_item(table_name))
        return transact_items

class UserCredentialPasswordUpdateEntity(UserCredentialEntity):
    """On password update, update
    self.failed_login_attempts =
    self.password_hash
    self.password_last_changed_datetime
    self.password_salt
    self.record_update_datetime
    """
    def __init__(self, update_user_credential_password_message:UpdateUserCredentialPasswordMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.username = update_user_credential_password_message.username                                # KEY

        password_utility = PasswordUtility()
        (sha256_hex, salt_b64) = password_utility.hash_password(password_text=update_user_credential_password_message.password)
        self.password_hash = sha256_hex
        self.password_last_changed_datetime = record_timestamp
        self.password_salt = salt_b64
        self.failed_login_attempts = '0'                        # UPDATE

        self.record_update_by = 'NOT SET'                       # UPDATE
        self.record_update_datetime = record_timestamp          # UPDATE

    # Components of update

    def __update_expression(self):
        return ('SET #FAILED_LOGIN_ATTEMPTS = :failed_login_attempts, '
                '#PASSWORD_HASH = :password_hash, '
                '#PASSWORD_LAST_CHANGED_DATETIME = :password_last_changed_datetime, '
                '#PASSWORD_SALT = :password_salt, '
                '#RECORD_UPDATE_BY = :record_update_by, '
                '#RECORD_UPDATE_DATETIME = :record_update_datetime')

    def __update_expression_attribute_names(self):
        return {
            '#FAILED_LOGIN_ATTEMPTS': 'failed_login_attempts',
            '#PASSWORD_HASH': 'password_hash',
            '#PASSWORD_LAST_CHANGED_DATETIME': 'password_last_changed_datetime',
            '#PASSWORD_SALT': 'password_salt',
            '#RECORD_UPDATE_BY': 'record_update_by',
            '#RECORD_UPDATE_DATETIME': 'record_update_datetime',
        }

    def __update_expression_attribute_values(self):
        return {
            ':failed_login_attempts': self.dynamodb_number_value('0'),
            ':password_hash': self.dynamodb_string_value(self.password_hash),
            ':password_last_changed_datetime': self.dynamodb_string_value(self.password_last_changed_datetime.isoformat()),
            ':password_salt': self.dynamodb_string_value(self.password_salt),
            ':record_update_by': self.dynamodb_string_value(self.record_update_by),
            ':record_update_datetime': self.dynamodb_string_value(self.record_update_datetime.isoformat())
        }

    def update_transact_item(self, table_name:str):
        return {
            'Update': {
                'TableName': table_name,
                'Key': {'username': {'S': self.username}},
                'UpdateExpression': self.__update_expression(),
                'ExpressionAttributeNames': self.__update_expression_attribute_names(),
                'ExpressionAttributeValues': self.__update_expression_attribute_values(),
                'ConditionExpression': 'attribute_exists(username)'
            }
        }

    def to_transact_items(self, table_name:str):
        transact_items = []
        transact_items.append(self.update_transact_item(table_name))
        return transact_items


# REPOSITORY CLASSES

class UserCredentialRepository(BaseRepository):
    """Repository for user_credential item
    Methods:
        add_user_credential
        authenticate_user_credential
    """
    def __init__(self):
        self._TABLE_NAME = 'user_credential'
        self.logger = logging.getLogger('UserCredentialRepository')
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        # ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s:  %(message)s"))
        self.logger.addHandler(ch)

    def add_user_credential(self, add_user_credential_message:AddUserCredentialMessage):
        try:
            response = dynamodb_client.put_item(
                TableName = self._TABLE_NAME,
                Item=AddUserCredentialEntity(add_user_credential_message).to_dynamodb_item(),
                ReturnConsumedCapacity='TOTAL',
                ConditionExpression="attribute_not_exists(username)",
            )
            self.logger.info('put_item: %s', response)
            # print('put_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            # print('client_error:', client_error)
            if 'Error' in client_error.response  \
                and 'Code' in client_error.response['Error'] \
                and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Record with username exists')
            return OperationResultMessage(False, client_error.response)

    def authenticate_user_credential(self, authenticate_user_credential_message:AuthenticateUserCredentialMessage):
        try:
            print('# authenticate_user_credential')
            print(f'Validating username: {authenticate_user_credential_message.username}')

            response = dynamodb_client.get_item(
                TableName=self._TABLE_NAME,
                Key={ 'username': {'S': authenticate_user_credential_message.username} }
            )

            print('authenticate_user_credential-Response', response)

            if 'Item' in response:
                user_credential_entity = UserCredentialEntity(response['Item'])

                salt_str = user_credential_entity.password_salt
                password_hash = user_credential_entity.password_hash

                password_utility = PasswordUtility()
                salt_bytes = password_utility.decode_base64_to_bytes(salt_str)
                (sha256_hex, salt_b64) = password_utility.hash_password(authenticate_user_credential_message.password, salt_bytes)

                is_valid_credentials = sha256_hex == password_hash

                if is_valid_credentials:
                    print('authenticate_user_credential-return', 'True: Valid credentials')
                    self.successful_login_update(authenticate_user_credential_message.username)
                    return OperationResultMessage(True, 'Credentials are authentic', {
                        'is_valid': True,
                        'message': 'Valid credentials'
                    })
                else:
                    print('authenticate_user_credential-return', 'False: Invalid credentials')
                    self.failed_login_update(authenticate_user_credential_message.username)
                    return OperationResultMessage(True, 'Credentials are not valid', {
                        'is_valid': False,
                        'message': 'Invalid credentials'
                    })

            print('authenticate_user_credential-return', 'False: User not found')
            return OperationResultMessage(True, 'User not found', {
                'is_valid': False,
                'message': 'User not found'
            })
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)

    def successful_login_update(self, username:str):
        """On successful login, update
        self.failed_login_attempts =
        self.last_login_attempt_datetime
        self.last_successful_login
        self.record_update_datetime
        """
        try:
            entity = SuccessfulLoginUserCredentialUpdateEntity(username)
            response = dynamodb_client.update_item(
                TableName=self._TABLE_NAME,
                Key=entity.update_item_key(),
                UpdateExpression=entity.update_item_update_expression(),
                ExpressionAttributeNames=entity.update_item_get_expression_attribute_names(),
                ExpressionAttributeValues=entity.update_item_expression_attribute_values(),
                ConditionExpression=entity.update_item_conditional_expression(),
                ReturnValues='ALL_NEW',
            )
            print('update_item:', response)
            if 'Attributes' in response:
                user_credential_entity = UserCredentialEntity(response['Attributes'])
                return OperationResultMessage(True, 'Successful login update completed.')
            return OperationResultMessage(True, 'Completed with no object returned')
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response \
                    and 'Code' in client_error.response['Error'] \
                    and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Item code does not exist or was returned')
            return OperationResultMessage(False, client_error.response)

    def failed_login_update(self, username:str):
        """On failed login, update
        self.failed_login_attempts =
        self.last_login_attempt_datetime
        self.last_successful_login
        self.record_update_datetime
        """
        try:
            entity = FailedLoginUserCredentialUpdateEntity(username)
            response = dynamodb_client.transact_write_items(TransactItems=entity.to_transact_items(self._TABLE_NAME))
            print('update_item:', response)
            # if 'Attributes' in response:
            #     user_credential_entity = UserCredentialEntity(response['Attributes'])
            #     return OperationResultMessage(True, 'Successful login update completed.')
            return OperationResultMessage(True, 'Completed with no object returned')
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response \
                    and 'Code' in client_error.response['Error'] \
                    and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Item code does not exist or was returned')
            return OperationResultMessage(False, client_error.response)

    def update_password(self, update_user_credential_password_message:UpdateUserCredentialPasswordMessage):
        """On updating password, update
        self.failed_login_attempts =
        self.password_hash
        self.password_last_changed_datetime
        self.password_salt
        self.record_update_datetime
        """
        try:
            entity = UserCredentialPasswordUpdateEntity(update_user_credential_password_message)
            response = dynamodb_client.transact_write_items(TransactItems=entity.to_transact_items(self._TABLE_NAME))
            print('update_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response \
                    and 'Code' in client_error.response['Error'] \
                    and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Item code does not exist or was returned')
            return OperationResultMessage(False, client_error.response)

    def get_user_credential_list(self, page_size:int=5, page_number:int=1, sort_field:str='username', sort_order:str='asc'):
        """
        List user credentials with pagination and sorting.

        Args:
            page_size (int): Number of items per page.
            page_number (int): Page number (1-based).
            sort_field (str): Field to sort by (default 'username').
            sort_order (str): 'asc' or 'desc' (default 'asc').

        Returns:
            dict: {
                'items': [UserCredentialEntity, ...],
                'last_evaluated_key': dict or None
            }
        """
        try:
            items = []
            scan_kwargs = {
                'TableName': self._TABLE_NAME,
                'ProjectionExpression': '#USERNAME, #STATUS, #FAILED_LOGIN_ATTEMPTS, #PASSWORD_LAST_CHANGED_DATETIME',
                'ExpressionAttributeNames': {
                    '#USERNAME': 'username',
                    '#STATUS': 'status',
                    '#FAILED_LOGIN_ATTEMPTS': 'failed_login_attempts',
                    '#PASSWORD_LAST_CHANGED_DATETIME' : 'password_last_changed_datetime'
                }
            }
            while True:
                response = dynamodb_client.scan(**scan_kwargs)
                items.extend(UserCredentialEntity(item).to_json_object(True) for item in response.get('Items', []))
                last_key = response.get('LastEvaluatedKey')
                if not last_key:
                    break
                scan_kwargs['ExclusiveStartKey'] = last_key

            reverse = sort_order.lower() == 'desc'
            items.sort(key=lambda record: record.get(sort_field), reverse=reverse)

            start = (page_number - 1) * page_size
            end = start + page_size

            return OperationResultMessage(True, None, data_object={
                'page_number': page_number,
                'page_size': page_size,
                'total_items': len(items),
                'page_items': items[start:end]
            })
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)

    def get_user_credential(self, username:str):
        """
        Get user credential

        Args:
            username (str): Username to retrieve.

        Returns:
            dict: {
                'items': [UserCredentialEntity, ...],
                'last_evaluated_key': dict or None
            }
        """
        try:
            response = dynamodb_client.get_item(
                TableName=self._TABLE_NAME,
                Key={'username': {'S': username}}
            )
            # print('get_item:', response)
            if 'Item' in response:
                entity = UserCredentialEntity(response['Item'])
                self.logger.info('get_item: %s', entity)
                return OperationResultMessage(
                    True,
                    'Retrieved user credential successfully',
                    data_object=UserCredentialEntity(response['Item']).to_json_object())
            return OperationResultMessage(True, 'User not found', data_object=None)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)

    def __remove_user_credential__(self, username:str):
        """
        Remove user credential

        Args:
            username (str): Username to retrieve.

        Returns:
            dict: {
                'items': [UserCredentialEntity, ...],
                'last_evaluated_key': dict or None
            }
        """
        try:
            response = dynamodb_client.delete_item(
                TableName=self._TABLE_NAME,
                Key={'username': {'S': username}},
                ConditionExpression="attribute_exists(username)"  # Ensure item exists before deleting
            )
            if 'ResponseMetadata' in response and 'HTTPStatusCode' in response['ResponseMetadata']:
                http_status_code = response['ResponseMetadata']['HTTPStatusCode']
                if http_status_code == 200:  # Successful deletion
                    return OperationResultMessage(True, 'User credential deleted successfully')
            return OperationResultMessage(False, 'Invalid response',
                                          data_object=response['ResponseMetadata']['HTTPStatusCode'])
            # pdb.set_trace()
            # if 'Item' in response:
            #     entity = UserCredentialEntity(response['Item'])
            #     return OperationResultMessage(
            #         True,
            #         data_object=UserCredentialEntity(response['Item']).to_json_object())
            # return OperationResultMessage(True, 'User not found', data_object=None)
            #
            # items = []
            # scan_kwargs = {
            #     'TableName': self._TABLE_NAME,
            #     'ProjectionExpression': '#USERNAME, #STATUS, #FAILED_LOGIN_ATTEMPTS, #PASSWORD_LAST_CHANGED_DATETIME',
            #     'ExpressionAttributeNames': {
            #         '#USERNAME': 'username',
            #         '#STATUS': 'status',
            #         '#FAILED_LOGIN_ATTEMPTS': 'failed_login_attempts',
            #         '#PASSWORD_LAST_CHANGED_DATETIME': 'password_last_changed_datetime'
            #     }
            # }
            # while True:
            #     # response = dynamodb_client.scan(**scan_kwargs)
            #     response = dynamodb_client.get_item(
            #         TableName=self._TABLE_NAME,
            #         Key={'id': {'S': username}}
            #     )
            #     items.extend(UserCredentialEntity(item).to_json_object(True) for item in response.get('Items', []))
            #     last_key = response.get('LastEvaluatedKey')
            #     if not last_key:
            #         break
            #     scan_kwargs['ExclusiveStartKey'] = last_key
            #
            # # reverse = sort_order.lower() == 'desc'
            # # items.sort(key=lambda record: record.get(sort_field), reverse=reverse)
            # #
            # # start = (page_number - 1) * page_size
            # # end = start + page_size
            #
            # return OperationResultMessage(True, None, data_object={
            #     'page_number': page_number,
            #     'page_size': page_size,
            #     'total_items': len(items),
            #     'page_items': items[start:end]
            # })
        except ClientError as client_error:
            # print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)

# TESTs


def test_repository():
    # Create message
    #add_user_credential_message = AddUserCredentialMessage('testuser2','testpass2')
    #authenticate_user_credential_message = AuthenticateUserCredentialMessage('testuser2', 'testpass2')
    #update_user_credential_password_message = UpdateUserCredentialPasswordMessage('testuser1', 'testuser1a')
    # Instantiate repository
    test_repository = UserCredentialRepository()
    # operation_result_message = test_repository.get_user_credential_list(page_number=1, page_size=50, sort_order='asc')
    # operation_result_message = test_repository.get_user_credential(username='testuser1')
    operation_result_message = test_repository.__remove_user_credential__(username='unittestuser')

    
    # Repository action
    #operation_result_message = test_repository.add_user_credential(add_user_credential_message)
    #operation_result_message = test_repository.authenticate_user_credential(authenticate_user_credential_message)
    #operation_result_message = test_repository.successful_login_update('testuser1')
    #operation_result_message = test_repository.failed_login_update('testuser1')
    #operation_result_message = test_repository.update_password(update_user_credential_password_message)
    print(operation_result_message)

if __name__ == '__main__':
    # Example
    test_repository()

