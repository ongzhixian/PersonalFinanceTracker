"""
Sections:
    Entity classes
        BaseRuleEntity
        SimpleRuleEntity
        NewSimpleRuleEntity
        AthenaQualityCheckRuleEntity
    Repository classes
        InventoryItemTable?
        BaseRepository
        InventoryItemRepository

"""
import json
from datetime import datetime, timezone, timedelta
from os import environ
from zoneinfo import ZoneInfo
import boto3
from botocore.exceptions import ClientError

from hci_data_repositories import DynamoDbEntity, BaseRepository
from hci_messages import OperationResultMessage, NewInventoryItemMessage, UpdateInventoryItemMessage, SuccessBorrowMessage

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
boto3.setup_default_session(profile_name=aws_profile)

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

# ENTITY CLASSES

## RULE ENTITY CLASSES

class BaseRuleEntity(DynamoDbEntity):
    """Base Quality Check Rule Item entity class.
    Inventory Item can have the following fields
    1. id
    1. rule_type
    1. is_enabled

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """
    def __init__(self):
        super().__init__()
        self.id = None
        self.rule_type = None
        self.is_enabled = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

    def to_dynamodb_item(self):
        item = {
            'id': self.dynamodb_null_value() if self.id is None else self.dynamodb_string_value(self.id),
            'rule_type': self.dynamodb_null_value() if self.rule_type is None else self.dynamodb_string_value(self.rule_type),
            'is_enabled': self.dynamodb_null_value() if self.is_enabled is None else self.dynamodb_string_value(self.is_enabled),

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

class SimpleRuleEntity(BaseRuleEntity):
    """A simple rule class.
    Inventory Item can have the following fields
    1. id
    1. rule_type
    1. is_enabled
    1. condition
    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """
    def __init__(self):
        super().__init__()
        self.condition = None

    def to_dynamodb_item(self):
        item = super().to_dynamodb_item() | {
            'condition': self.dynamodb_null_value() if self.condition is None else self.dynamodb_string_value(self.condition),
        }
        return item

class NewSimpleRuleEntity(SimpleRuleEntity):
    def __init__(self, message:NewInventoryItemMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()
        self.item_code = message.item_code
        self.item_description = message.item_code

        self.record_update_by = message.user_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = message.user_code
        self.record_create_datetime = record_timestamp


class AthenaQualityCheckRuleEntity(BaseRuleEntity):
    """Base Quality Check Rule Item entity class.
    Inventory Item can have the following fields
    1. test_id
    1. data_source
    1. query
    1. failure_template

    1. severity
    1. effective_from
    1. effective_to

    1. test_name
    1. stage_name
    1. cron_settings
    1. is_enabled

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """
    def __init__(self):
        super().__init__()
        self.test_id = None
        self.data_source = None
        self.query = None
        self.failure_template = None

        self.severity = None
        self.effective_from = None
        self.effective_to = None

        self.test_name = None
        self.stage_name = None
        self.cron_settings = None
        self.is_enabled = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

    def to_dynamodb_item(self):
        item = super().to_dynamodb_item() | {
            'test_id': self.dynamodb_null_value() if self.test_id is None else self.dynamodb_string_value(self.test_id),
            'data_source': self.dynamodb_null_value() if self.data_source is None else self.dynamodb_string_value(self.data_source),
            'query': self.dynamodb_null_value() if self.query is None else self.dynamodb_string_value(self.query),
            'failure_template': self.dynamodb_null_value() if self.failure_template is None else self.dynamodb_string_value(self.failure_template),

            'severity': self.dynamodb_null_value() if self.severity is None else self.dynamodb_string_value(self.severity),
            'effective_from': self.dynamodb_null_value() if self.effective_from is None else self.dynamodb_string_value(self.effective_from.isoformat()),
            'effective_to': self.dynamodb_null_value() if self.effective_to is None else self.dynamodb_string_value(self.effective_to.isoformat()),

            'test_name': self.dynamodb_null_value() if self.test_name is None else self.dynamodb_string_value(self.test_name),
            'stage_name': self.dynamodb_null_value() if self.stage_name is None else self.dynamodb_string_value(self.stage_name),
            'cron_settings': self.dynamodb_null_value() if self.cron_settings is None else self.dynamodb_string_value(self.cron_settings),
            'is_enabled': self.dynamodb_null_value() if self.is_enabled is None else self.dynamodb_string_value(self.is_enabled),
        }
        return item


# class NewInventoryItemEntity(InventoryItemEntity):
#     def __init__(self, message:NewInventoryItemMessage):
#         super().__init__()
#         record_timestamp = self.get_record_timestamp()
#         self.item_code = message.item_code
#         self.item_description = message.item_code
#
#         self.record_update_by = message.user_code
#         self.record_update_datetime = record_timestamp
#         self.record_create_by = message.user_code
#         self.record_create_datetime = record_timestamp
#
# class BorrowInventoryItemEntity(InventoryItemEntity):
#     def __init__(self, message:UpdateInventoryItemMessage):
#         super().__init__()
#         record_timestamp = self.get_record_timestamp()
#
#         self.item_code = message.item_code                      # KEY
#         self.borrow_by = message.borrower_code                  # UPDATE
#         self.borrow_datetime = record_timestamp                 # UPDATE
#         self.due_datetime = record_timestamp + timedelta(14)    # UPDATE
#
#         self.record_update_by = message.user_code               # UPDATE
#         self.record_update_datetime = record_timestamp          # UPDATE
#
#     # Components of update
#
#     def update_item_key(self):
#         return {
#             'item_code': {'S': self.item_code}
#         }
#
#     def update_item_update_expression(self) -> str:
#         return 'SET #BORROW_BY = :borrow_by, #BORROW_DATETIME = :borrow_datetime, #DUE_DATETIME = :due_datetime, #RECORD_UPDATE_BY = :record_update_by, #RECORD_UPDATE_DATETIME = :record_update_datetime'
#
#     def update_item_get_expression_attribute_names(self):
#         return {
#             '#BORROW_BY'                : 'borrow_by',
#             '#BORROW_DATETIME'          : 'borrow_datetime',
#             '#DUE_DATETIME'             : 'due_datetime',
#             '#RECORD_UPDATE_BY'         : 'record_update_by',
#             '#RECORD_UPDATE_DATETIME'   : 'record_update_datetime',
#         }
#
#     def update_item_expression_attribute_values(self):
#         return {
#             ':borrow_by'                : {'S': self.borrow_by},
#             ':borrow_datetime'          : {'S': self.borrow_datetime.isoformat() },
#             ':due_datetime'             : {'S': self.due_datetime.isoformat(), },
#             ':record_update_by'         : {'S': self.record_update_by, },
#             ':record_update_datetime'   : {'S': self.record_update_datetime.isoformat(), },
#             ':type_is_null'             : {'S': 'NULL'},
#         }
#
#     def update_item_conditional_expression(self):
#         return "attribute_type(borrow_by, :type_is_null)"
#
# class ReturnInventoryItemEntity(InventoryItemEntity):
#     def __init__(self, message:UpdateInventoryItemMessage):
#         super().__init__()
#         record_timestamp = self.get_record_timestamp()
#
#         self.item_code = message.item_code                      # KEY
#         # self.borrow_by = message.borrower_code                  # UPDATE
#         # self.borrow_datetime = record_timestamp                 # UPDATE
#         # self.due_datetime = record_timestamp + timedelta(14)    # UPDATE
#         self.record_update_by = message.user_code               # UPDATE
#         self.record_update_datetime = record_timestamp          # UPDATE
#
#     # Components of update
#
#     def update_item_key(self):
#         return {
#             'item_code': {'S': self.item_code}
#         }
#
#     def update_item_update_expression(self) -> str:
#         return 'SET #BORROW_BY = :borrow_by, #BORROW_DATETIME = :borrow_datetime, #DUE_DATETIME = :due_datetime, #RECORD_UPDATE_BY = :record_update_by, #RECORD_UPDATE_DATETIME = :record_update_datetime'
#
#     def update_item_get_expression_attribute_names(self):
#         return {
#             '#BORROW_BY'                : 'borrow_by',
#             '#BORROW_DATETIME'          : 'borrow_datetime',
#             '#DUE_DATETIME'             : 'due_datetime',
#             '#RECORD_UPDATE_BY'         : 'record_update_by',
#             '#RECORD_UPDATE_DATETIME'   : 'record_update_datetime',
#         }
#
#     def update_item_expression_attribute_values(self):
#         return {
#             ':borrow_by'                : {'NULL': True},
#             ':borrow_datetime'          : {'NULL': True},
#             ':due_datetime'             : {'NULL': True},
#             ':record_update_by'         : {'S': self.record_update_by, },
#             ':record_update_datetime'   : {'S': self.record_update_datetime.isoformat(), },
#             ':type_is_null'             : {'S': 'NULL'},
#             ':item_code'                : {'S': self.item_code},
#         }
#
#     def update_item_conditional_expression(self):
#         return "NOT attribute_type(borrow_by, :type_is_null) and item_code = :item_code"
#

# REPOSITORY CLASSES

class RuleRepository(BaseRepository):
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

