import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='default')

class BaseDynamoDbRepository(object):
    """Base repository class for DynamoDb"""

    def __init__(self):
        self.client = boto3.client('dynamodb')

    def get_table_list(self) -> list:
        response = self.client.list_tables()
        return response['TableNames']

    def table_exists(self, table_name:str) -> bool:
        return table_name in self.get_table_list()
    
    def delete_table(self, table_name:str) -> None:
        # Note: Table deletion are not instantaneous.
        #       The initial status would be 'DELETING'
        response = self.client.delete_table(TableName=table_name)
        # print(response)
        # return True

    # def get_table(self, table_name:str) -> None:
    #     response = client.describe_table(TableName=table_name)
    #     print(response)


class UserCredentialRepository(BaseDynamoDbRepository):
    """DynamoDb repository for UserCredential"""

    def __init__(self):
        self.TABLE_NAME = 'user_credential'

    def create_table_if_not_exists(self):
        response = self.client.create_table(
            TableName=self.TABLE_NAME,
            AttributeDefinitions=[
                  { 'AttributeName': 'username'     , 'AttributeType': 'S' }
                , { 'AttributeName': 'SongTitle'  , 'AttributeType': 'S' }
            ],
            KeySchema=[
                  { 'AttributeName': 'username'     , 'KeyType': 'HASH' }
                , { 'AttributeName': 'SongTitle'  , 'KeyType': 'RANGE'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        print(response)

    def put_record(self):
        response = self.client.put_item(
            TableName=self.TABLE_NAME,
            Item={
                'username'      : { 'S': 'Somewhat Famous' },
                'password_hash' : { 'S': 'No One You Know' },
                'password_salt'         : { 'S': 'Call Me Today'},
                'failed_login_attempts' : {'S': 'Call Me Today'},
            },
            ReturnConsumedCapacity='TOTAL'
        )
        print(response)

    def get_record(self):
        pass
        response = self.client.get_item(
            Key={
                'Artist': {
                    'S': 'Acme Band',
                },
                'SongTitle': {
                    'S': 'Happy Day',
                },
            },
            TableName='Music',
        )

        print(response)

    def get_record_list(self):
        response = self.client.scan(
            ExpressionAttributeNames={
                '#AT': 'AlbumTitle',
                '#ST': 'SongTitle',
            },
            ExpressionAttributeValues={
                ':a': {
                    'S': 'No One You Know',
                },
            },
            FilterExpression='Artist = :a',
            ProjectionExpression='#ST, #AT',
            TableName='Music',
        )

        print(response)

    def find_record(self):
        pass
        response = self.client.query(
            ExpressionAttributeValues={
                ':v1': {
                    'S': 'No One You Know',
                },
            },
            KeyConditionExpression='Artist = :v1',
            ProjectionExpression='SongTitle',
            TableName='Music',
        )

        print(response)

    def delete_record(self):
        response = self.client.delete_item(
            Key={
                'Artist': {
                    'S': 'No One You Know',
                },
                'SongTitle': {
                    'S': 'Scared of My Shadow',
                },
            },
            TableName='Music',
        )

        print(response)
