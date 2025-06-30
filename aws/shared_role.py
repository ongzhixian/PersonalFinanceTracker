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

from shared_configuration import ConfigurationRepository
from shared_configuration_messages import ResertConfigurationMessage

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
    1. name
    1. description
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
        """
        Load data from a dictionary into the RoleEntity instance.
        Note: Role is stored within a single entity in Configuration;
              So we read directly from the dictionary keys instead of using self.map_from_dynamodb_attribute() function
        """
        self.name = data[RoleEntity.NAME_FIELD_NAME] if RoleEntity.NAME_FIELD_NAME in data else None
        self.description = data[RoleEntity.DESCRIPTION_FIELD_NAME] if RoleEntity.DESCRIPTION_FIELD_NAME in data else None
        self.status = data[RoleEntity.STATUS_FIELD_NAME] if RoleEntity.STATUS_FIELD_NAME in data else None

        self.record_update_by = data[RoleEntity.RECORD_UPDATE_BY_FIELD_NAME] if RoleEntity.RECORD_UPDATE_BY_FIELD_NAME in data else None
        self.record_update_datetime = data[RoleEntity.RECORD_UPDATE_BY_FIELD_NAME] if RoleEntity.RECORD_UPDATE_BY_FIELD_NAME in data else None
        self.record_create_by = data[RoleEntity.RECORD_CREATE_BY_FIELD_NAME] if RoleEntity.RECORD_CREATE_BY_FIELD_NAME in data else None
        self.record_create_datetime = data[RoleEntity.RECORD_CREATE_DATETIME_FIELD_NAME] if RoleEntity.RECORD_CREATE_DATETIME_FIELD_NAME in data else None


    def __str__(self):
        """human-readable, informal string representation"""
        return (f"{RoleEntity.NAME_FIELD_NAME}: {self.name}, "
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

    @staticmethod
    def json_type_convertor(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to string
        raise TypeError(f"Type {type(obj)} not serializable")


class AddRoleEntity(RoleEntity):
    """(Re)place or In(sert) a configuration record."""

    def __init__(self, add_user_credential_message: AddRoleMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.name = add_user_credential_message.name
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
        self._TABLE_RECORD_ID = 'UCM_ROLE_LIST'
        self.configuration_repository = ConfigurationRepository()

    def json_type_convertor(obj):
        """
        Custom JSON encoder
        Consider putting this in a shared module
        """
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to string
        raise TypeError(f"Type {type(obj)} not serializable")

    def update_role(self, role_entity: RoleEntity):
        try:
            # Get role list record
            role_list_record = self._get_underlying_role_list_record()
            role_list = role_list_record.get('roles', {})

            # Add entry to role_list data object
            json_object = role_entity.to_json_object()
            role_key = self._derive_key_from_name(role_entity.name)
            role_list[role_key] = json_object

            # Store updated role_list data object
            message = ResertConfigurationMessage(
                record_id=self._TABLE_RECORD_ID,
                content_type='JSON',
                content=json.dumps(role_list_record, default=RoleEntity.json_type_convertor),
                user_code='SYSTEM_TEST')
            return self.configuration_repository.resert_configuration(message)

            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response \
                    and 'Code' in client_error.response['Error'] \
                    and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Record with username exists')
            return OperationResultMessage(False, client_error.response)

    def add_role(self, add_role_message: AddRoleMessage):
        try:
            # Get role list record
            role_list_record = self._get_underlying_role_list_record()
            role_list = role_list_record.get('roles', {})

            # Add entry to role_list data object
            json_object = AddRoleEntity(add_role_message).to_json_object()
            role_key = self._derive_key_from_name(add_role_message.name)
            role_list[role_key] = json_object

            # Store updated role_list data object
            message = ResertConfigurationMessage(
                record_id=self._TABLE_RECORD_ID,
                content_type='JSON',
                content=json.dumps(role_list_record, default=RoleEntity.json_type_convertor),
                user_code='SYSTEM_TEST')
            return self.configuration_repository.resert_configuration(message)

            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response \
                    and 'Code' in client_error.response['Error'] \
                    and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Record with username exists')
            return OperationResultMessage(False, client_error.response)

    def delete_role(self, role_name: str):
        try:
            # Get role list record
            role_list_record = self._get_underlying_role_list_record()
            role_list = role_list_record.get('roles', {})
            role_key = self._derive_key_from_name(role_name)

            # Remove entry from role_list data object
            if role_key in role_list:
                del role_list[role_key]

            # Store updated role_list data object
            message = ResertConfigurationMessage(
                record_id=self._TABLE_RECORD_ID,
                content_type='JSON',
                content=json.dumps(role_list_record, default=RoleEntity.json_type_convertor),
                user_code='SYSTEM_TEST')
            return self.configuration_repository.resert_configuration(message)

            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response \
                    and 'Code' in client_error.response['Error'] \
                    and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Record with username exists')
            return OperationResultMessage(False, client_error.response)

    def get_role_list(self):
        try:
            items = self._get_underlying_role_list_record()
            return OperationResultMessage(True, None, data_object=items)

        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)

    def get_role(self, role_name: str):
        """
        Get role by name.

        Args:
            role_name (str): Name of the role to retrieve.

        Returns:
            OperationResultMessage: Result of the operation, containing the role entity if successful.
        """
        try:
            items = self._get_underlying_role_list_record()
            roles = items.get('roles', {})
            role_key = self._derive_key_from_name(role_name)

            if role_key in roles:
                role_data = roles[role_key]
                role_entity = RoleEntity(role_data)
                return OperationResultMessage(True, None, data_object=role_entity)

            return OperationResultMessage(False, f'Role {role_name} not found')

        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)

    def _derive_key_from_name(self, name: str) -> str:
        """Convert name to a key suitable for use in a database
        Returns:
            str: Key representation of the name
        """
        return name.lower().replace(' ', '_')

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

        operation_result_message = self.configuration_repository.get_configuration(self._TABLE_RECORD_ID)
        print('operation_result_message', operation_result_message)
        if operation_result_message.is_success and operation_result_message.data_object is not None:
            items = operation_result_message.data_object['content']

        return items
        #
        # response = dynamodb_client.get_item(
        #     TableName=self._TABLE_NAME,
        #     Key={
        #         'id': {'S': self._TABLE_RECORD_ID}
        #     }
        # )
        #
        # if 'Item' in response:
        #     role_list = json.loads(response['Item']['content']['S'])
        #     role_list['roles'] = dict(sorted(
        #         role_list['roles'].items(),
        #         key=lambda item: item[0],
        #         reverse=True
        #     ))
        #     items = role_list


# TESTs


def test_repository():
    # Create message
    # add_user_credential_message = AddUserCredentialMessage('testuser2','testpass2')
    # authenticate_user_credential_message = AuthenticateUserCredentialMessage('testuser2', 'testpass2')
    # update_user_credential_password_message = UpdateUserCredentialPasswordMessage('testuser1', 'testuser1a')

    # Instantiate repository
    test_repository = RoleRepository()

    # Add some new role
    # add_role_message = AddRoleMessage('TESTER', 'Tester role')
    # test_repository.add_role(add_role_message)

    # Get specific role
    # operation_result_message = test_repository.get_role('TESTER')
    # tester_data_object: RoleEntity = operation_result_message.data_object
    # print(vars(tester_data_object))

    # Simulate updating a role
    # tester_data_object.description = 'Tester role for development'
    # test_repository.update_role(tester_data_object)

    # Simulate deleting a role
    # test_repository.delete_role('TESTERDEL')

    operation_result_message = test_repository.get_role_list()
    print('\noperation_result_message', operation_result_message)

    role_list = operation_result_message.data_object['roles']
    print('Role keys:', list(role_list.keys()))


if __name__ == '__main__':
    # Example
    test_repository()

