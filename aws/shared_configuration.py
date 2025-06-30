"""
Sections:
    AWS Setup
    Entity classes
        ConfigurationEntity
        ResertConfigurationEntity
    Repository classes
        ConfigurationRepository
"""
import json
from datetime import datetime
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

import boto3
from botocore.exceptions import ClientError

from shared_data_repositories import DynamoDbEntity, BaseRepository
from shared_messages import OperationResultMessage
from shared_configuration_messages import ResertConfigurationMessage

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

class ConfigurationEntity(DynamoDbEntity):
    """Base Configuration entity class.
    A Configuration record can have the following fields
    1. id
    1. content_type
    1. content

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """

    ID_FIELD_NAME = 'id'
    CONTENT_TYPE_FIELD_NAME = 'content_type'
    CONTENT_FIELD_NAME = 'content'

    RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
    RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
    RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'


    def __init__(self, *args, **kwargs):
        super().__init__()
        self.id = None
        self.content_type = None
        self.content = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

        if len(args) > 0 and isinstance(args[0], dict):
            self.load_from_dict(args[0])

    def to_dynamodb_item(self):
        item = {
            'id': self.dynamodb_null_value() if self.id is None else self.dynamodb_string_value(self.id),
            'content_type': self.dynamodb_null_value() if self.content_type is None else self.dynamodb_string_value(self.content_type),
            'content': self.dynamodb_null_value() if self.content is None else self.dynamodb_string_value(self.content),
            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

    def load_from_dict(self, data:dict):
        self.id = self.map_from_dynamodb_attribute(data, ConfigurationEntity.ID_FIELD_NAME)
        self.content_type = self.map_from_dynamodb_attribute(data, ConfigurationEntity.CONTENT_TYPE_FIELD_NAME)
        content = self.map_from_dynamodb_attribute(data, ConfigurationEntity.CONTENT_FIELD_NAME)
        match self.content_type:
            case 'JSON':
                self.content = json.loads(content)
            case 'TEXT':
                self.content = content
            case _:
                self.content = content

        self.record_update_by = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_update_datetime = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_UPDATE_DATETIME_FIELD_NAME)
        self.record_create_by = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_CREATE_BY_FIELD_NAME)
        self.record_create_datetime = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_CREATE_DATETIME_FIELD_NAME)

    def __str__(self):
        """human-readable, informal string representation"""
        return (f"{ConfigurationEntity.ID_FIELD_NAME}: {self.id}, "
                f"{ConfigurationEntity.CONTENT_TYPE_FIELD_NAME}: {self.content_type},"
                f" {ConfigurationEntity.CONTENT_FIELD_NAME}: {self.content}, ")

    def __repr__(self):
        """unambiguous, developer-friendly string representation"""
        return json.dumps(self.__dict__)
        # return json.dumps({
        #     ConfigurationEntity.ID_FIELD_NAME : self.id,
        #     ConfigurationEntity.CONTENT_TYPE_FIELD_NAME: self.content_type,
        #     ConfigurationEntity.CONTENT_FIELD_NAME: self.content,
        #     ConfigurationEntity.RECORD_UPDATE_BY_FIELD_NAME: self.record_update_by,
        #     ConfigurationEntity.RECORD_UPDATE_DATETIME_FIELD_NAME: self.record_update_datetime,
        #     ConfigurationEntity.RECORD_CREATE_BY_FIELD_NAME: self.record_create_by,
        #     ConfigurationEntity.RECORD_CREATE_DATETIME_FIELD_NAME: self.record_create_datetime
        # })

    def to_json_object(self):
        return self.__dict__

    @staticmethod
    def get_record_timestamp() -> datetime:
        # record_timestamp = datetime.now(timezone.utc).as timezone(SINGAPORE_TIMEZONE)
        record_timestamp = datetime.now(SINGAPORE_TIMEZONE)
        return record_timestamp

class ResertConfigurationEntity(ConfigurationEntity):
    """(Re)place or In(sert) a configuration record."""
    def __init__(self, resert_configuration_message:ResertConfigurationMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()
        self.id = resert_configuration_message.id
        self.content_type = resert_configuration_message.content_type
        self.content = resert_configuration_message.content

        self.record_update_by = resert_configuration_message.user_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = resert_configuration_message.user_code
        self.record_create_datetime = record_timestamp


# REPOSITORY CLASSES

class ConfigurationRepository(BaseRepository):
    """Repository for inventory item
    Methods:
        add_new_inventory_item
    """
    def __init__(self):
        self.CONFIGURATION_TABLE_NAME = 'configuration'

    def resert_configuration(self, resert_configuration_message:ResertConfigurationMessage):
        try:
            response = dynamodb_client.put_item(
                TableName = self.CONFIGURATION_TABLE_NAME,
                Item=ResertConfigurationEntity(resert_configuration_message).to_dynamodb_item(),
                ReturnConsumedCapacity='TOTAL'
            )
            print('put_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')

    def get_configuration(self, record_id:str):
        try:
            response = dynamodb_client.get_item(
                TableName=self.CONFIGURATION_TABLE_NAME,
                Key={'id': {'S': record_id}
                }
            )
            print('get_item:', response)
            if 'Item' in response:
                # data_obj = self.__data_object_from_dynamodb_response_item(response['Item'])
                # message = BaseConfigurationMessage()
                # message.load_dynamodb_item(response['Item'])
                # entity = ConfigurationEntity(response['Item'])
                return OperationResultMessage(
                    True,
                    data_object=ConfigurationEntity(response['Item']).to_json_object())
            return OperationResultMessage(True)

        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')

    def get_all_configurations(self):
        try:
            response = dynamodb_client.scan(TableName=self.CONFIGURATION_TABLE_NAME)
            print('scan:', response)
            if 'Items' in response:
                result = []
                for item in response['Items']:
                    # Transform response['Item'] back into JSON-compatible object
                    # message = BaseConfigurationMessage()
                    # message.load_dynamodb_item(item)
                    result.append(ConfigurationEntity(item).to_json_object())
                return OperationResultMessage(True, data_object=result)
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error'


def main():
    # Example
    configuration_repository = ConfigurationRepository()
    # message = ResertConfigurationMessage(
    #     record_id='SYSTEM_TEST_01',
    #     content_type='JSON',
    #     content=json.dumps({
    #         'environment': {
    #             'development': {
    #                 'version': 10
    #             },
    #             'production': {
    #                 'version': 3
    #             }
    #         }
    #     }),
    #     user_code='SYSTEM_TEST')
    message = ResertConfigurationMessage(
        record_id='UCM_ROLES',
        content_type='JSON',
        content=json.dumps({
            'roles': {
                'guest': {
                    'name': 'Guest User',
                    'description': 'Limited access for public viewing.',
                    'actions': ['read_public_reports'],
                    'status': 'active'
                },
                'membership_editor': {
                    'name': 'Membership Editor',
                    'description': 'Can create, edit, and publish content.',
                    'actions': ['read_membership', 'write_membership', 'list_membership'],
                    'status': 'active'
                },
                'user_credential_editor': {
                    'name': 'User Credential Editor',
                    'description': 'Can create, edit, and publish user credential.',
                    'actions': ['read_user_credential', 'write_user_credential', 'list_user_credential'],
                    'status': 'active'
                }
            }
        }),
        user_code='SYSTEM_TEST')
    message = ResertConfigurationMessage(
        record_id='UCM_SECRETS',
        content_type='JSON',
        content=json.dumps({
            'authentication_token': {
                'value': 'some-secret-value',
                'entry_datetime': '2025-05-27',
            }
        }),
        user_code='SYSTEM_TEST')
    configuration_repository.resert_configuration(message)

    # operation_result_message = configuration_repository.get_configuration('SYSTEM_TEST_01')
    # print(operation_result_message)
    # data_object = operation_result_message.data_object
    # print(operation_result_message.data_object)
    # print(json.dumps(operation_result_message.data_object))

    operation_result_message = configuration_repository.get_all_configurations()
    data_object_list = operation_result_message.data_object
    print(len(data_object_list))
    print(data_object_list)


def main2():
    configuration_repository = ConfigurationRepository()
    # operation_result_message = configuration_repository.get_all_configurations()
    operation_result_message = configuration_repository.get_configuration('UCM_ROLE_LIST')
    print('\noperation_result_message', operation_result_message)

if __name__ == '__main__':
    #main()
    main2()