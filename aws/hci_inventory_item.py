from datetime import datetime, timezone
from os import environ
from zoneinfo import ZoneInfo
import boto3

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
boto3.setup_default_session(profile_name=aws_profile)

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

class DynamoDbEntity(object):
    pass

class InventoryItemEntity(DynamoDbEntity):
    """Inventory Item can have the following fields
    1. item_code
    1. item_description
    1. borrower_code
    1. borrow_datetime
    1. due_datetime
    1. record_update_by
    1. record_update_datetime
    """
    def __init__(self):
        super().__init__()
        self.item_code = None
        self.item_description = None
        self.borrower_code = None
        self.borrow_datetime = None
        self.due_datetime = None
        self.record_update_by = None
        self.record_update_datetime = None

class NewInventoryItemEntity(InventoryItemEntity):
    def __init__(self, item_code:str, update_by:str):
        super().__init__()
        self.item_code = item_code
        self.record_update_by = update_by
        self.record_update_datetime = datetime.now(SINGAPORE_TIMEZONE)
        #self.record_update_datetime = datetime.now(timezone.utc).astimezone(SINGAPORE_TIMEZONE)


class InventoryItemTable(object):
    """
    # PRIVATE FUNCTIONS
    # 1. __create_table
    # 2. __delete_table
    """
    def __init__(self):
        self.TABLE_NAME = 'hci_inventory_item'

    # PRIVATE FUNCTIONS

    def __create_table(self):
        response = dynamodb_client.create_table(
            TableName=self.TABLE_NAME,
            AttributeDefinitions=[
                {'AttributeType': 'S', 'AttributeName': 'item_code'}
            ],
            KeySchema=[
                {'AttributeName': 'item_code', 'KeyType': 'HASH'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        print(response)

    def __delete_table(self):
        response = dynamodb_client.delete_table(TableName=self.TABLE_NAME)
        print(response)

    # PUBLIC FUNCTIONS
    # 1. put_inventory_item
    # 1. borrow_inventory_item
    # 1. return_inventory_item

    def put_new_inventory_item_from(self, entity:NewInventoryItemEntity):
        """
        """
        response = dynamodb_client.put_item(
            TableName=self.TABLE_NAME,
            Item={
                'item_code': {'S': entity.item_code},
                'item_description': {'S': entity.item_description},
                'borrower_code': {'NULL': True} if entity.borrower_code is None else {'S': entity.borrower_code },
                'borrow_datetime': {'NULL': True},
                'target_return_datetime': {'NULL': True},
            },
            ReturnConsumedCapacity='TOTAL'
        )
        print(response)

    def put_new_inventory_item(self, item_code: str, item_description: str):
        """
        """
        response = dynamodb_client.put_item(
            TableName=self.TABLE_NAME,
            Item={
                'item_code': {'S': item_code},
                'item_description': {'S': item_description},
                'borrower_code': {'NULL': True},
                'borrow_datetime': {'NULL': True},
                'target_return_datetime': {'NULL': True},
            },
            ReturnConsumedCapacity='TOTAL'
        )
        print(response)