"""
Sections:
    AWS Setup
    Entity classes
        RoleEntity
        AddRoleEntity
    Repository classes
        RoleRepository
"""
import json
from datetime import datetime
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

import boto3
from botocore.exceptions import ClientError

from utility_types import PasswordUtility
from shared_data_repositories import DynamoDbEntity, BaseRepository
from shared_messages import OperationResultMessage
from shared_role_messages import AddRoleMessage

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

class RoleEntity(DynamoDbEntity):
    """Base Role entity class.
    A role record can have the following fields:
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

    NAME_FIELD_NAME = 'name'
    DESCRIPTION_FIELD_NAME = 'description'
    STATUS_FIELD_NAME = 'status'

    RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
    RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
    RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'

    private_fields = [
        'record_update_by',
        'record_update_datetime',
        'record_create_by',
        'record_create_datetime']

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.name = None
        self.description = None
        self.status = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

        if len(args) > 0 and isinstance(args[0], dict):
            self.load_from_dict(args[0])

    def to_dynamodb_item(self):
        item = {
            'name': self.dynamodb_null_value() if self.name is None else self.dynamodb_string_value(self.name),
            'description': self.dynamodb_null_value() if self.description is None else self.dynamodb_string_value(self.description),
            'status': self.dynamodb_null_value() if self.status is None else self.dynamodb_string_value(self.status),

            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

    def load_from_dict(self, data: dict):
        self.username = self.map_from_dynamodb_attribute(data, RoleEntity.NAME_FIELD_NAME)
        self.description = self.map_from_dynamodb_attribute(data, RoleEntity.DESCRIPTION_FIELD_NAME)
        self.status = self.map_from_dynamodb_attribute(data, RoleEntity.STATUS_FIELD_NAME)

        self.record_update_by = self.map_from_dynamodb_attribute(data, RoleEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_update_datetime = self.map_from_dynamodb_attribute(data, RoleEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_create_by = self.map_from_dynamodb_attribute(data, RoleEntity.RECORD_CREATE_BY_FIELD_NAME)
        self.record_create_datetime = self.map_from_dynamodb_attribute(data, RoleEntity.RECORD_CREATE_DATETIME_FIELD_NAME)

    def __str__(self):
        """human-readable, informal string representation"""
        return (f"{RoleEntity.USERNAME_FIELD_NAME}: {self.username}, "
                f"{RoleEntity.STATUS_FIELD_NAME}: {self.status}")

    # def __repr__(self):
    #     """unambiguous, developer-friendly string representation"""
    #     return json.dumps(self.__dict__)

    def to_json_object(self, public_only=False):
        if public_only:
            for field_name in RoleEntity.private_fields:
                self.__dict__.pop(field_name)

        return self.__dict__

    @staticmethod
    def get_record_timestamp() -> datetime:
        # record_timestamp = datetime.now(timezone.utc).as timezone(SINGAPORE_TIMEZONE)
        record_timestamp = datetime.now(SINGAPORE_TIMEZONE)
        return record_timestamp


class AddRoleEntity(RoleEntity):
    """(Re)place or In(sert) a configuration record."""

    def __init__(self, add_user_credential_message: AddRoleMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.username = add_user_credential_message.username
        self.description = add_user_credential_message.description
        self.status = add_user_credential_message.status

        self.record_update_by = 'NOT SET'
        self.record_update_datetime = record_timestamp
        self.record_create_by = 'NOT SET'
        self.record_create_datetime = record_timestamp


# REPOSITORY CLASSES

class RoleRepository(BaseRepository):
    """Repository for role item
    Methods:
        add_role
        get_role_list
    """

    def __init__(self):
        self._TABLE_NAME = 'configuration'
        self._TABLE_RECORD_ID = 'UCM_ROLE_LIST'
        # self._TABLE_RECORD_ID = 'UCM_ROLES'

    def add_role(self, add_role_message: AddRoleMessage):
        try:
            # Get role list record
            role_list = self._get_underlying_role_list_record()
            # Add entry to role_list data object
            role_key = add_role_message.name.lower().replace(' ', '_')
            role_list[role_key] = {
                "name": add_role_message.name,
                "description": add_role_message.name,
                "status": 'active'
            }
            # Store updated role_list data object


            response = dynamodb_client.put_item(
                TableName=self._TABLE_NAME,
                Item=AddRoleEntity(add_role_message).to_dynamodb_item(),
                ReturnConsumedCapacity='TOTAL',
                ConditionExpression="attribute_not_exists(username)",
            )
            # print('put_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response \
                    and 'Code' in client_error.response['Error'] \
                    and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Record with username exists')
            return OperationResultMessage(False, client_error.response)


    def _get_underlying_role_list_record(self):
        """
        List role sorted by role name in alphabetical order.

        Returns:
            dict: {
                'items': [UserCredentialEntity, ...],
                'last_evaluated_key': dict or None
            }
        """

        items = {
            "roles": {}
        }

        response = dynamodb_client.get_item(
            TableName=self._TABLE_NAME,
            Key={
                'id': {'S': self._TABLE_RECORD_ID}
            }
        )

        if 'Item' in response:
            role_list = json.loads(response['Item']['content']['S'])
            role_list['roles'] = dict(sorted(
                role_list['roles'].items(),
                key=lambda item: item[0],
                reverse=True
            ))
            items = role_list
        return items


    def get_role_list(self):
        try:
            items = self._get_underlying_role_list_record()
            return OperationResultMessage(True, None, data_object=items)

        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)

# TESTs


def test_repository():
    # Create message
    # add_user_credential_message = AddUserCredentialMessage('testuser2','testpass2')
    # authenticate_user_credential_message = AuthenticateUserCredentialMessage('testuser2', 'testpass2')
    # update_user_credential_password_message = UpdateUserCredentialPasswordMessage('testuser1', 'testuser1a')
    add_role_message = AddRoleMessage('TESTER', 'Tester role')


    # Instantiate repository
    test_repository = RoleRepository()
    operation_result_message = test_repository.get_role_list()
    test_repository.add_role(add_role_message)
    # operation_result_message = test_repository.get_user_credential_list(page_number=1, sort_order='asc')

    # Repository action
    # operation_result_message = test_repository.add_user_credential(add_user_credential_message)
    # operation_result_message = test_repository.authenticate_user_credential(authenticate_user_credential_message)
    # operation_result_message = test_repository.successful_login_update('testuser1')
    # operation_result_message = test_repository.failed_login_update('testuser1')
    # operation_result_message = test_repository.update_password(update_user_credential_password_message)
    print(operation_result_message)


if __name__ == '__main__':
    # Example
    test_repository()

