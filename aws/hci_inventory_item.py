"""
Sections:
    Entity classes
        InventoryItemEntity
        NewInventoryItemEntity
    Repository classes
        InventoryItemTable?
        BaseRepository
        InventoryItemRepository

"""
import json
from datetime import datetime, timedelta
from os import environ
from zoneinfo import ZoneInfo
import boto3
from botocore.exceptions import ClientError

from hci_messages import NewInventoryItemMessage, UpdateInventoryItemMessage
from shared_messages import OperationResultMessage
from shared_data_repositories import DynamoDbEntity, BaseRepository

import pdb

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
boto3.setup_default_session(profile_name=aws_profile)

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

# ENTITY CLASSES

## INVENTORY ITEM ENTITY CLASSES

class InventoryItemEntity(DynamoDbEntity):
    """Base Inventory Item entity class.
    Inventory Item can have the following fields
    1. item_code
    1. item_description
    1. borrow_by
    1. borrow_datetime
    1. due_datetime

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """
    ITEM_CODE_FIELD_NAME = 'item_code'
    ITEM_DESCRIPTION_FIELD_NAME = 'item_description'
    BORROW_BY_FIELD_NAME = 'borrow_by'
    BORROW_DATETIME_FIELD_NAME = 'borrow_datetime'
    DUE_DATETIME_FIELD_NAME = 'due_datetime'

    RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
    RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
    RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'

    def __init__(self, data:dict|None):
        super().__init__()
        self.item_code = None
        self.item_description = None
        self.borrow_by = None
        self.borrow_datetime = None
        self.due_datetime = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

        if data is not None:
            self.load_from_dict(data)

    def to_dynamodb_item(self):
        item = {
            'item_code': self.dynamodb_null_value() if self.item_code is None else self.dynamodb_string_value(self.item_code),
            'item_description': self.dynamodb_null_value() if self.item_description is None else self.dynamodb_string_value(self.item_description),
            'borrow_by': self.dynamodb_null_value() if self.borrow_by is None else self.dynamodb_string_value(self.borrow_by),
            'borrow_datetime': self.dynamodb_null_value() if self.borrow_datetime is None else self.dynamodb_string_value(self.borrow_datetime.isoformat()),
            'due_datetime': self.dynamodb_null_value() if self.due_datetime is None else self.dynamodb_string_value(self.due_datetime.isoformat()),
            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

    def load_from_dict(self, data:dict):
        self.item_code = self.map_from_dynamodb_attribute(data, InventoryItemEntity.ITEM_CODE_FIELD_NAME)
        self.item_description = self.map_from_dynamodb_attribute(data, InventoryItemEntity.ITEM_DESCRIPTION_FIELD_NAME)
        self.borrow_by = self.map_from_dynamodb_attribute(data, InventoryItemEntity.BORROW_BY_FIELD_NAME)
        self.borrow_datetime = self.map_from_dynamodb_attribute(data, InventoryItemEntity.BORROW_DATETIME_FIELD_NAME)
        self.due_datetime = self.map_from_dynamodb_attribute(data, InventoryItemEntity.DUE_DATETIME_FIELD_NAME)
        self.record_update_by = self.map_from_dynamodb_attribute(data, InventoryItemEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_update_datetime = self.map_from_dynamodb_attribute(data, InventoryItemEntity.RECORD_UPDATE_DATETIME_FIELD_NAME)
        self.record_create_by = self.map_from_dynamodb_attribute(data, InventoryItemEntity.RECORD_CREATE_BY_FIELD_NAME)
        self.record_create_datetime = self.map_from_dynamodb_attribute(data, InventoryItemEntity.RECORD_CREATE_DATETIME_FIELD_NAME)

    def to_json_object(self):
        return self.__dict__

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

    @staticmethod
    def get_record_timestamp() -> datetime:
        # record_timestamp = datetime.now(timezone.utc).as timezone(SINGAPORE_TIMEZONE)
        record_timestamp = datetime.now(SINGAPORE_TIMEZONE)
        return record_timestamp


class NewInventoryItemEntity(InventoryItemEntity):
    def __init__(self, message:NewInventoryItemMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()
        self.item_code = message.item_code
        self.item_description = message.item_code

        self.record_update_by = message.user_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = message.user_code
        self.record_create_datetime = record_timestamp

class BorrowInventoryItemEntity(InventoryItemEntity):
    def __init__(self, message:UpdateInventoryItemMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.item_code = message.item_code                      # KEY
        self.borrow_by = message.borrower_code                  # UPDATE
        self.borrow_datetime = record_timestamp                 # UPDATE
        self.due_datetime = record_timestamp + timedelta(14)    # UPDATE

        self.record_update_by = message.user_code               # UPDATE
        self.record_update_datetime = record_timestamp          # UPDATE

    # Components of update

    def update_item_key(self):
        return {
            'item_code': {'S': self.item_code}
        }

    def update_item_update_expression(self) -> str:
        return 'SET #BORROW_BY = :borrow_by, #BORROW_DATETIME = :borrow_datetime, #DUE_DATETIME = :due_datetime, #RECORD_UPDATE_BY = :record_update_by, #RECORD_UPDATE_DATETIME = :record_update_datetime'

    def update_item_get_expression_attribute_names(self):
        return {
            '#BORROW_BY'                : 'borrow_by',
            '#BORROW_DATETIME'          : 'borrow_datetime',
            '#DUE_DATETIME'             : 'due_datetime',
            '#RECORD_UPDATE_BY'         : 'record_update_by',
            '#RECORD_UPDATE_DATETIME'   : 'record_update_datetime',
        }

    def update_item_expression_attribute_values(self):
        return {
            ':borrow_by'                : {'S': self.borrow_by},
            ':borrow_datetime'          : {'S': self.borrow_datetime.isoformat() },
            ':due_datetime'             : {'S': self.due_datetime.isoformat(), },
            ':record_update_by'         : {'S': self.record_update_by, },
            ':record_update_datetime'   : {'S': self.record_update_datetime.isoformat(), },
            ':type_is_null'             : {'S': 'NULL'},
        }

    def update_item_conditional_expression(self):
        return "attribute_type(borrow_by, :type_is_null)"

class ReturnInventoryItemEntity(InventoryItemEntity):
    def __init__(self, message:UpdateInventoryItemMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.item_code = message.item_code                      # KEY
        # self.borrow_by = message.borrower_code                  # UPDATE
        # self.borrow_datetime = record_timestamp                 # UPDATE
        # self.due_datetime = record_timestamp + timedelta(14)    # UPDATE
        self.record_update_by = message.user_code               # UPDATE
        self.record_update_datetime = record_timestamp          # UPDATE

    # Components of update

    def update_item_key(self):
        return {
            'item_code': {'S': self.item_code}
        }

    def update_item_update_expression(self) -> str:
        return 'SET #BORROW_BY = :borrow_by, #BORROW_DATETIME = :borrow_datetime, #DUE_DATETIME = :due_datetime, #RECORD_UPDATE_BY = :record_update_by, #RECORD_UPDATE_DATETIME = :record_update_datetime'

    def update_item_get_expression_attribute_names(self):
        return {
            '#BORROW_BY'                : 'borrow_by',
            '#BORROW_DATETIME'          : 'borrow_datetime',
            '#DUE_DATETIME'             : 'due_datetime',
            '#RECORD_UPDATE_BY'         : 'record_update_by',
            '#RECORD_UPDATE_DATETIME'   : 'record_update_datetime',
        }

    def update_item_expression_attribute_values(self):
        return {
            ':borrow_by'                : {'NULL': True},
            ':borrow_datetime'          : {'NULL': True},
            ':due_datetime'             : {'NULL': True},
            ':record_update_by'         : {'S': self.record_update_by, },
            ':record_update_datetime'   : {'S': self.record_update_datetime.isoformat(), },
            ':type_is_null'             : {'S': 'NULL'},
            ':item_code'                : {'S': self.item_code},
        }

    def update_item_conditional_expression(self):
        return "NOT attribute_type(borrow_by, :type_is_null) and item_code = :item_code"


# REPOSITORY CLASSES

class InventoryItemRepository(BaseRepository):
    """Repository for inventory item
    Methods:
        add_new_inventory_item
    """
    def __init__(self):
        self.INVENTORY_ITEM_TABLE_NAME = 'hci_inventory_item'

    def add_new_inventory_item(self, message:NewInventoryItemMessage):
        try:
            response = dynamodb_client.put_item(
                TableName = self.INVENTORY_ITEM_TABLE_NAME,
                Item=NewInventoryItemEntity(message).to_dynamodb_item(),
                ConditionExpression="attribute_not_exists(item_code)",
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

    def __make_borrow_record(self, attributes):
        pass

    def __map_from_dynamodb_attribute(self, att:dict):
        for k, v in att.items():
            match k:
                case 'S':
                    return v
                case "N":
                    return float(v)
                case _:
                    print(f'Unhandled DynamoDb attribute {k}')
                    return None
        print('No DynamoDb attribute')
        return None

    def __borrow_inventory_item(self, message:UpdateInventoryItemMessage):
        try:
            entity = BorrowInventoryItemEntity(message)
            response = dynamodb_client.update_item(
                TableName=self.INVENTORY_ITEM_TABLE_NAME,
                Key=entity.update_item_key(),
                UpdateExpression=entity.update_item_update_expression(),
                ExpressionAttributeNames=entity.update_item_get_expression_attribute_names(),
                ExpressionAttributeValues=entity.update_item_expression_attribute_values(),
                ConditionExpression=entity.update_item_conditional_expression(),
                ReturnValues='ALL_NEW',
            )
            print('update_item:', response)

            borrow_record = None
            if 'Attributes' in response:
                # dict(
                #     map(lambda kv:
                #         (kv[0], str(kv[1])),
                #         self.__dict__.items()
                #     )
                # )

                #borrow_record = self.__make_borrow_record(response['Attributes'])
                #print('att', response['Attributes'])
                # successBorrowMessage = SuccessBorrowMessage(response['Attributes'])
                borrow_record = dict(
                    map(lambda kv:
                        (kv[0], self.__map_from_dynamodb_attribute(kv[1])),
                        response['Attributes'].items()
                    )
                )
                print('borrow_record', borrow_record)
            return OperationResultMessage(True, 'Borrow success', data_object=borrow_record)
        except ClientError as client_error:
            print('client_error:', client_error)
            print('client_error_response:', json.dumps(client_error.response))
            if 'Error' in client_error.response  \
                and 'Code' in client_error.response['Error'] \
                and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Item code does not exist or was borrowed')
                # "Error": {
                #     "Message": "The conditional request failed",
                #     "Code": "ConditionalCheckFailedException"
                # },

            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')

    def __return_inventory_item(self, message: UpdateInventoryItemMessage):
        try:
            entity = ReturnInventoryItemEntity(message)
            response = dynamodb_client.update_item(
                TableName=self.INVENTORY_ITEM_TABLE_NAME,
                Key=entity.update_item_key(),
                UpdateExpression=entity.update_item_update_expression(),
                ExpressionAttributeNames=entity.update_item_get_expression_attribute_names(),
                ExpressionAttributeValues=entity.update_item_expression_attribute_values(),
                ConditionExpression=entity.update_item_conditional_expression(),
                ReturnValues='ALL_NEW',
            )
            print('update_item:', response)
            return_record = None
            if 'Attributes' in response:
                return_record = dict(
                    map(lambda kv:
                        (kv[0], self.__map_from_dynamodb_attribute(kv[1])),
                        response['Attributes'].items()
                        )
                )
                print('return_record', return_record)
            return OperationResultMessage(True, 'Return success', data_object=return_record)
        except ClientError as client_error:
            print('client_error:', client_error)
            if 'Error' in client_error.response  \
                and 'Code' in client_error.response['Error'] \
                and client_error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return OperationResultMessage(False, 'Item code does not exist or was returned')
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')

    def __extend_borrow_inventory_item(self, message: UpdateInventoryItemMessage):
        """KIV: Future nice to have feature"""
        return OperationResultMessage(False, '`extend_borrow` message handler not implemented')
        try:
            entity = BorrowInventoryItemEntity(message)
            response = dynamodb_client.update_item(
                TableName=self.INVENTORY_ITEM_TABLE_NAME,
                Key=entity.update_item_key(),
                UpdateExpression=entity.update_item_update_expression(),
                ExpressionAttributeNames=entity.update_item_get_expression_attribute_names(),
                ExpressionAttributeValues=entity.update_item_expression_attribute_values(),
                ConditionExpression=entity.update_item_conditional_expression(),
                ReturnValues='ALL_NEW',
            )
            print('update_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')

    def update_inventory_item(self, message:UpdateInventoryItemMessage):
        if message.is_borrow_message():
            return self.__borrow_inventory_item(message)

        if message.is_return_message():
            return self.__return_inventory_item(message)

        if message.is_extend_borrow_message():
            return self.__extend_borrow_inventory_item(message)

        return OperationResultMessage(False, 'No matching message handler')

    def get_all_inventory_item(self):
        try:
            result = []
            scan_kwargs = {
                'TableName': self.INVENTORY_ITEM_TABLE_NAME
            }
            while True:
                response = dynamodb_client.scan(**scan_kwargs)
                # print('scan:', response)
                if 'Items' in response:
                    for item in response['Items']:
                        result.append(InventoryItemEntity(item).to_json_object())
                if 'LastEvaluatedKey' not in response:
                    break
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

            # Sort
            result.sort(key=lambda r: r['item_code'], reverse=False)
            return OperationResultMessage(True, data_object=result)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, error=client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error'


if __name__ == "__main__":
    inventory_item_repository = InventoryItemRepository()
    operation_result_message = inventory_item_repository.get_all_inventory_item()
    item_list = operation_result_message.data_object
    print(len(item_list))
    pdb.set_trace()


    # Create items script
    # for num in range(1, 15 + 1):
    #     item_code = f'HS(14) - XL{num:02d}'
    #     print(item_code)
    #     message = NewInventoryItemMessage(item_code=item_code, user_code='zhixian@hotmail.com')
    #     inventory_item_repository.add_new_inventory_item(message)
