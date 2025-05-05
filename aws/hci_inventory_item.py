"""
Sections:
    Base Entity classes
        DynamoDbEntity
    Entity classes
        InventoryItemEntity
        NewInventoryItemEntity
    Repository classes
        InventoryItemTable?
        BaseRepository
        InventoryItemRepository

"""
from datetime import datetime, timezone, timedelta
from os import environ
from zoneinfo import ZoneInfo
import boto3
from botocore.exceptions import ClientError

from hci_messages import OperationResultMessage, NewInventoryItemMessage, UpdateInventoryItemMessage

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
boto3.setup_default_session(profile_name=aws_profile)

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

# BASE ENTITY CLASSES

class DynamoDbEntity(object):

    @staticmethod
    def dynamodb_null_value():
        return {'NULL': True}

    @staticmethod
    def dynamodb_string_value(value):
        return {'S': value}


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
    def __init__(self):
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

    def get_record_timestamp(self) -> datetime:
        # record_timestamp = datetime.now(timezone.utc).as timezone(SINGAPORE_TIMEZONE)
        record_timestamp = datetime.now(SINGAPORE_TIMEZONE)
        return record_timestamp


class NewInventoryItemEntity(InventoryItemEntity):
    def __init__(self, message:NewInventoryItemMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()
        self.item_code = message.item_code
        self.item_description = message.item_code

        self.record_update_by = message.actor_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = message.actor_code
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

    def update_item_update_expression(self):
        return 'SET #BORROWER_CODE = :borrower_code, #BORROW_DATETIME = :borrow_datetime, #DUE_DATETIME = :due_datetime, #RECORD_UPDATE_BY = :record_update_by, #RECORD_UPDATE_DATETIME = :record_update_datetime',

    def update_item_get_expression_attribute_names(self):
        return {
            '#BORROWER_CODE'    : 'borrower_code',
            '#BORROW_DATETIME'  : 'borrow_datetime',
            '#DUE_DATETIME'     : 'due_datetime',
            '#UPDATE_BY'        : 'record_update_by',
            '#UPDATE_DATETIME'  : 'record_update_datetime',
        }

    def update_item_expression_attribute_values(self):
        return {
            ':borrower_code'            : {'S': self.borrow_by},
            ':borrow_datetime'          : {'S': self.borrow_datetime.isoformat() },
            ':due_datetime'             : {'S': self.due_datetime.isoformat(), },
            ':record_update_by'         : {'S': self.record_update_by, },
            ':record_update_datetime'   : {'S': self.record_update_datetime.isoformat(), },
            ':type_is_null'             : {'S': 'NULL'},
        }

    def update_item_conditional_expression(self):
        return "attribute_type(borrower_code, :type_is_null)"

# REPOSITORY CLASSES
#
# class InventoryItemTable(object):
#     """
#     # PRIVATE FUNCTIONS
#     # 1. __create_table
#     # 2. __delete_table
#     """
#     def __init__(self):
#         self.TABLE_NAME = 'hci_inventory_item'
#
#     # PRIVATE FUNCTIONS
#
#     def __create_table(self):
#         response = dynamodb_client.create_table(
#             TableName=self.TABLE_NAME,
#             AttributeDefinitions=[
#                 {'AttributeType': 'S', 'AttributeName': 'item_code'}
#             ],
#             KeySchema=[
#                 {'AttributeName': 'item_code', 'KeyType': 'HASH'}
#             ],
#             ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
#         )
#         print(response)
#
#     def __delete_table(self):
#         response = dynamodb_client.delete_table(TableName=self.TABLE_NAME)
#         print(response)
#
#     # PUBLIC FUNCTIONS
#     # 1. put_inventory_item
#     # 1. borrow_inventory_item
#     # 1. return_inventory_item
#
#     def put_new_inventory_item_from(self, entity:NewInventoryItemEntity):
#         """
#         """
#         response = dynamodb_client.put_item(
#             TableName=self.TABLE_NAME,
#             Item={
#                 'item_code': {'S': entity.item_code},
#                 'item_description': {'S': entity.item_description},
#                 'borrower_code': {'NULL': True} if entity.borrower_code is None else {'S': entity.borrower_code },
#                 'borrow_datetime': {'NULL': True},
#                 'target_return_datetime': {'NULL': True},
#             },
#             ReturnConsumedCapacity='TOTAL'
#         )
#         print(response)
#
#     def put_new_inventory_item(self, item_code: str, item_description: str):
#         """
#         """
#         response = dynamodb_client.put_item(
#             TableName=self.TABLE_NAME,
#             Item={
#                 'item_code': {'S': item_code},
#                 'item_description': {'S': item_description},
#                 'borrower_code': {'NULL': True},
#                 'borrow_datetime': {'NULL': True},
#                 'target_return_datetime': {'NULL': True},
#             },
#             ReturnConsumedCapacity='TOTAL'
#         )
#         print(response)

class BaseRepository(object):
    pass
    # def __list_tables(self):
    #     response = dynamodb_client.list_tables()
    #     return response
    #
    # def __create_inventory_item_table(self):
    #     response = dynamodb_client.create_table(
    #         TableName='hci_inventory_item',
    #         AttributeDefinitions=[
    #             {'AttributeType': 'S', 'AttributeName': 'item_code'},
    #             {'AttributeType': 'S', 'AttributeName': 'item_description'},
    #         ],
    #         KeySchema=[
    #             {'AttributeName': 'item_code', 'KeyType': 'HASH'},
    #             {'AttributeName': 'item_description', 'KeyType': 'RANGE'},
    #         ],
    #         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    #     )
    #     print(response)
    #
    # def __delete_table(self, table_name: str):
    #     response = dynamodb_client.delete_table(TableName=table_name)
    #     print(response)


###



class InventoryItemRepository(BaseRepository):
    """Repository for inventory item
    Methods:
        add_new_inventory_item
    """
    def __init__(self):
        self.INVENTORY_ITEM_TABLE_NAME = 'hci_inventory_item'
        pass

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
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')


    def __return_inventory_item(self, message: UpdateInventoryItemMessage):
        return OperationResultMessage(False, '`return` message handler not implemented')
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

    def __extend_borrow_inventory_item(self, message: UpdateInventoryItemMessage):
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
