"""
Sections:
    AWS Setup
    Entity classes
        CounterEntity
        ResertCounterEntity
    Repository classes
        CounterRepository
"""
import json
from datetime import datetime
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

import boto3
from botocore.exceptions import ClientError

from shared_data_repositories import DynamoDbEntity, BaseRepository
from shared_messages import OperationResultMessage
from shared_counter_messages import ResertCounterMessage, IncrementCounterMessage

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

## COUNTER ENTITY CLASSES

class CounterEntity(DynamoDbEntity):
    """Base Counter entity class.
    A counter record can have the following fields
    1. id
    1. value
    1. description

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """

    ID_FIELD_NAME = 'id'
    VALUE_FIELD_NAME = 'value'
    DESCRIPTION_FIELD_NAME = 'description'

    RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
    RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
    RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.id = None
        # self.value_type = None
        self.value = None
        self.description = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

        if len(args) > 0 and isinstance(args[0], dict):
            self.load_from_dict(args[0])

    def to_dynamodb_item(self):
        """
        """
        item = {
            'id': self.dynamodb_null_value() if self.id is None else self.dynamodb_string_value(self.id),
            'value': self.dynamodb_null_value() if self.value is None else self.dynamodb_number_value(self.value),
            'description': self.dynamodb_null_value() if self.description is None else self.dynamodb_string_value(self.description),

            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

    def load_from_dict(self, data:dict):
        self.id = self.map_from_dynamodb_attribute(data, CounterEntity.ID_FIELD_NAME)
        # self.value_type = self.map_from_dynamodb_attribute(data, CounterEntity.VALUE_TYPE_FIELD_NAME)
        self.value = self.map_from_dynamodb_attribute(data, CounterEntity.VALUE_FIELD_NAME)
        self.description = self.map_from_dynamodb_attribute(data, CounterEntity.DESCRIPTION_FIELD_NAME)

        self.record_update_by = self.map_from_dynamodb_attribute(data, CounterEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_update_datetime = self.map_from_dynamodb_attribute(data, CounterEntity.RECORD_UPDATE_DATETIME_FIELD_NAME)
        self.record_create_by = self.map_from_dynamodb_attribute(data, CounterEntity.RECORD_CREATE_BY_FIELD_NAME)
        self.record_create_datetime = self.map_from_dynamodb_attribute(data, CounterEntity.RECORD_CREATE_DATETIME_FIELD_NAME)

    def __str__(self):
        """human-readable, informal string representation"""
        return (f"{CounterEntity.ID_FIELD_NAME}: {self.id}, "
                f"{CounterEntity.DESCRIPTION_FIELD_NAME}: {self.description}")

    def __repr__(self):
        """unambiguous, developer-friendly string representation"""
        return json.dumps(self.__dict__)

    def to_json_object(self):
        return self.__dict__

    @staticmethod
    def get_record_timestamp() -> datetime:
        # record_timestamp = datetime.now(timezone.utc).as timezone(SINGAPORE_TIMEZONE)
        record_timestamp = datetime.now(SINGAPORE_TIMEZONE)
        return record_timestamp

class ResertCounterEntity(CounterEntity):
    """(Re)place or In(sert) a counter record."""
    def __init__(self, resert_counter_message:ResertCounterMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.id = resert_counter_message.id
        self.value = resert_counter_message.value
        self.description = resert_counter_message.description

        self.record_update_by = resert_counter_message.user_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = resert_counter_message.user_code
        self.record_create_datetime = record_timestamp

class IncrementCounterEntity(CounterEntity):
    """Increment a counter record."""
    def __init__(self, increment_counter_message:IncrementCounterMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()
        self.increment_value = increment_counter_message.increment

        self.id = increment_counter_message.id

        self.record_update_by = increment_counter_message.user_code
        self.record_update_datetime = record_timestamp

    def __update_expression(self):
        return 'ADD #value :incr_value SET #record_update_by = :record_update_by, #record_update_datetime = :record_update_datetime'

    def __update_expression_attribute_names(self):
        return {
            '#value': 'value',
            '#record_update_by': 'record_update_by',
            '#record_update_datetime': 'record_update_datetime',
        }

    def __update_expression_attribute_values(self):
        return {
            ':incr_value': self.dynamodb_number_value(str(self.increment_value)),
            ':record_update_by': self.dynamodb_string_value(self.record_update_by),
            ':record_update_datetime': self.dynamodb_string_value(self.record_update_datetime.isoformat())
        }


    def update_transact_item(self, table_name:str):
        return {
            'Update': {
                'TableName': table_name,
                'Key': {'id': {'S': self.id}},
                'UpdateExpression': self.__update_expression(),
                'ExpressionAttributeNames': self.__update_expression_attribute_names(),
                'ExpressionAttributeValues': self.__update_expression_attribute_values(),
                'ConditionExpression': 'attribute_exists(id)'
            }
        }

    def to_transact_items(self, table_name:str):
        transact_items = []
        transact_items.append(self.update_transact_item(table_name))
        return transact_items


# REPOSITORY CLASSES

class CounterRepository(BaseRepository):
    """Repository for counter item
    Methods:
        resert_counter
    """
    def __init__(self):
        self._TABLE_NAME = 'counter'

    def resert_counter(self, resert_configuration_message:ResertCounterMessage):
        put_item_kwargs = {
            'TableName' : self._TABLE_NAME,
            'Item': ResertCounterEntity(resert_configuration_message).to_dynamodb_item(),
            'ReturnConsumedCapacity': 'TOTAL',
            #'ConditionExpression': 'attribute_not_exists(id)'
        }
        try:
            response = dynamodb_client.put_item(**put_item_kwargs)
            #print('put_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            error = client_error.response['Error'] if 'Error' in client_error.response else None

            if error is None: return OperationResultMessage(False, client_error.response)

            error_code = error['Code'] if 'Code' in error else None
            match error_code:
                case 'ConditionalCheckFailedException':
                    return OperationResultMessage(
                        False,
                        f"Error code: {error_code}, ConditionExpression: {put_item_kwargs['ConditionExpression']}",
                        data_object=resert_configuration_message)
                case _:
                    return OperationResultMessage(False, error)

    def update_counter(self, increment_counter_message:IncrementCounterMessage):
        entity = IncrementCounterEntity(increment_counter_message)
        try:
            # Note: We cannot mix SET, REMOVE, ADD, DELETE in Dynamodb update expression
            #       But we can mix them in a UPDATE transact item!
            response = dynamodb_client.transact_write_items(TransactItems=entity.to_transact_items(self._TABLE_NAME))
            print('update_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            error = client_error.response['Error'] if 'Error' in client_error.response else None
            if error is None: return OperationResultMessage(False, client_error.response)
            error_code = error['Code'] if 'Code' in error else None
            print('error', error)
            match error_code:
                case 'TransactionCanceledException':
                    return OperationResultMessage(
                        operation_is_successful=False,
                        message=f"Error code: {error_code}, Error message: {error['Message']}",
                        data_object=client_error.response['CancellationReasons'])
                case _:
                    return OperationResultMessage(False, error)
        except Exception as exception:
            print(exception)

    def get_counter_name_list(self):
        try:
            result = []
            scan_kwargs = {
                'TableName': self._TABLE_NAME,
                'ProjectionExpression': '#ID',
                'ExpressionAttributeNames': {
                    '#ID': 'id',
                }
            }
            while True:
                response = dynamodb_client.scan(**scan_kwargs)
                print('scan:', response)
                if 'Items' in response:
                    for item in response['Items']:
                        result.append(DynamoDbEntity.get_dynamodb_attribute_value(item, CounterEntity.ID_FIELD_NAME))
                if 'LastEvaluatedKey' not in response:
                    break
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

            # Sort
            result.sort(key=lambda r: r, reverse=False)
            return OperationResultMessage(True, data_object=result)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, error=client_error.response)

    def get_all_counters(self):
        try:
            result = []
            scan_kwargs = {
                'TableName': self._TABLE_NAME,
                'ProjectionExpression': '#ID, #DESCRIPTION, #VALUE',
                'ExpressionAttributeNames': {
                    '#ID': 'id',
                    '#DESCRIPTION': 'description',
                    '#VALUE': 'value',
                }
            }
            while True:
                response = dynamodb_client.scan(**scan_kwargs)
                print('scan:', response)
                if 'Items' in response:
                    for item in response['Items']:
                        result.append(CounterEntity(item).to_json_object())
                if 'LastEvaluatedKey' not in response:
                    break
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

            # Sort
            result.sort(key=lambda r: r['id'], reverse=False)
            return OperationResultMessage(True, data_object=result)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, error=client_error.response)

    def get_counter_by_scan(self, counter_name: str):
        try:
            result = []
            scan_kwargs = {
                'TableName': self._TABLE_NAME,
                'FilterExpression': '#ID = :id',
                'ExpressionAttributeNames': {
                    '#ID': 'id',
                },
                'ExpressionAttributeValues': {
                    ':id': { 'S': counter_name },
                }
            }
            while True:
                response = dynamodb_client.scan(**scan_kwargs)
                print('scan:', response)
                if 'Items' in response:
                    for item in response['Items']:
                        result.append(CounterEntity(item).to_json_object())
                if 'LastEvaluatedKey' not in response:
                    break
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

            # Sort
            result.sort(key=lambda r: r['id'], reverse=False)
            if len(result) <= 0:
                return OperationResultMessage(True)
            return OperationResultMessage(True, data_object=result[0])
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, error=client_error.response)

    def get_counter(self, counter_name: str):
        try:
            response = dynamodb_client.get_item(
                TableName = self._TABLE_NAME,
                Key = {
                    'id': { 'S': counter_name }
                }
            )

            if 'Item' in response:
                retrieved_counter_entity = CounterEntity(response['Item']).to_json_object()
                return OperationResultMessage(True, data_object=retrieved_counter_entity)
            else:
                return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, error=client_error.response)

    def add_to_counter(self, counter_name: str, increment:int):
        message = IncrementCounterMessage(
            id=counter_name,
            user_code='SYSTEM_TEST',
            increment=increment)
        self.update_counter(message)


# TESTs

def test_counter_repository():
    counter_list2 = [
        'successful-job', 'failed-job', 'test-counter', 'running-job',
        'pending-job', 'completed-job', 'testCounter1'
    ]
    counter_list = ['testCounter1']

    counter_repository = CounterRepository()
    # for counter_name in counter_list:
    #     message = ResertCounterMessage(
    #         id=counter_name,
    #         description='TEST COUNTER',
    #         user_code = 'SYSTEM_TEST')
    #     operation_result_message = counter_repository.resert_counter(message)
    #     print('Updated:', counter_name)

    # print(operation_result_message)
    # message = IncrementCounterMessage(
    #     id='testCounter2',
    #     user_code='SYSTEM_TEST')
    # counter_repository.update_counter(message)

    # rule = counter_repository.get_rule('generic_1')
    # print(rule)
    counter_name_list = counter_repository.get_counter_name_list()
    print(counter_name_list)

if __name__ == '__main__':
    # Example
    test_counter_repository()
