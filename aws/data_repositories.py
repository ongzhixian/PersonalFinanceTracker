"""
This module contains the following classes:

1.  BaseDynamoDbModel
1.  BaseDynamoDbRepository
1.  UserCredentialRepository
"""

import os
import logging
from time import time
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError, WaiterError
from utility_types import PasswordUtility

########################################
# SETUP AWS PROFILE

runtime_dns_domain = os.environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else 'default'
boto3.setup_default_session(profile_name=aws_profile)

from message_types import CreateUserCredentialMessage, UserCredentialPasswordUpdateMessage, LoginMessage
from record_types import UserCredentialRecord, InsertUserCredentialRecord, UpdateUserCredentialPasswordRecord


########################################
# BaseDynamoDbRepository

class BaseDynamoDbRepository(object):
    """Base repository class for DynamoDb

---------1---------2---------3---------4---------5---------6---------7--
    This is the base class that classes following the repository pattern
     for DynamoDB inherit from.

    Contains the following methods:

    1.  __setup_logging

    And waiters (because the AWS SDK does not have async-await):

    1.  wait_for_table_exists
    1.  wait_for_table_not_exists

    Table operations: (GET-CHECKS-ADD-UPDATE-REMOVE)

    1.  get_table_list
    1.  table_exists
    1.  table_in_use
    1.  delete_table

    Code review:

        1. Remove print statements and replace them with logging
        1. Maybe move setting of table name to base class

    """

    def __init__(self, table_name: str, client=None):
        self.TABLE_NAME = table_name
        self.client = boto3.client('dynamodb') if client is None else client
        self.__setup_logging(logging.DEBUG)

    def __setup_logging(self, logging_level):
        ch = logging.StreamHandler()
        ch.setLevel(logging_level)
        ch.setFormatter(logging.Formatter('[%(levelname).3s] %(asctime)s %(name)s - %(message)s'))
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(ch)
        self.log.setLevel(logging_level)

    # def get_table(self) -> None:
    #     """Helper function """
    #     response = self.client.describe_table(TableName=self.TABLE_NAME)
    #     print(response)

    # Waiters

    def wait_for_table_exists(self, delay: float = 1, max_attempts: int = 25):
        """Waits for a table to come into existence ('ACTIVE')

        :param delay:
            Wait constraint dictating interval (in seconds) to poll for
            table

        :param max_attempts:
            Wait constraint dictating how times to poll for the table

        :return:
            None ->
                if table come into existence within the wait constraints

            WaiterError ->
                if table did not come into existence within the wait
                constraints

        """
        try:
            waiter = self.client.get_waiter('table_exists')
            waiter.wait(TableName=self.TABLE_NAME, WaiterConfig={
                'Delay': delay,
                'MaxAttempts': max_attempts
            })
        except WaiterError as waiter_error:
            return waiter_error.last_response

    def wait_for_table_not_exists(self, delay: float = 1, max_attempts: int = 25):
        """Waits for a table to be removed

        :param delay:
            Wait constraint dictating interval (in seconds) to poll for
            table

        :param max_attempts:
            Wait constraint dictating how times to poll for the table

        :return:
            None ->
                if table was removed within the wait constraints

            WaiterError ->
                if table was not removed within the wait constraints

        """
        try:
            waiter = self.client.get_waiter('table_not_exists')
            waiter.wait(TableName=self.TABLE_NAME, WaiterConfig={
                'Delay': delay,
                'MaxAttempts': max_attempts
            })
        except WaiterError as waiter_error:
            return waiter_error.last_response

    # Table Operations

    def get_table_list(self) -> list:
        """Gets a list of DynamoDb tables
        :return:
            List[str] ->
                List of table names

        """
        response = self.client.list_tables()
        return response['TableNames']

    def table_exists(self) -> bool:
        """Checks if table exists

        :return:
            True ->
                if table exists
            False ->
                if table does not exist
        """
        in_list = self.TABLE_NAME in self.get_table_list()
        return in_list

    def table_in_use(self) -> bool:
        """
        Identifies if table is being affected by AWS.

        A DynamoDb table may have 3 states:
        1. 'ACTIVE'   -- An existing table
        1. 'CREATING' -- Table that is being provisioned by AWS
        1. 'DELETING' -- Table that is being removed by AWS

        :return:
            True ->
                if table is in 'CREATING' or 'DELETING' state
            False ->
                if table does not exist
                --OR--
                if table is not in 'ACTIVE' state
        """
        if not self.table_exists():
            self.log.debug('Table %s does not exists', self.TABLE_NAME)
            return False

        response = self.client.describe_table(TableName=self.TABLE_NAME)
        table = response['Table']
        table_status = table['TableStatus']
        self.log.debug('table_status is %s', table_status)
        return False if table_status == 'ACTIVE' else True

    def delete_table(self, table_name: str) -> None:
        """Delete a table

        :param table_name:
            Name of table to delete

        :return:
        """
        t0 = time()
        try:
            if self.table_in_use():
                self.log.warning('Table %s is in use. Table deletion stopped.', table_name)
                return
            response = self.client.delete_table(TableName=table_name)
            # Table deletion is not instantaneous.
            # So by default, the table status would have been 'DELETING'.
            # When the table is deleted, it no longer exists.
            # There is no await, so we use a waiter.
            table_description = response['TableDescription']
            table_status = table_description['TableStatus']
            if table_status == 'DELETING':
                waiter = self.client.get_waiter('table_not_exists')
                self.wait_for_table_not_exists()
            t1 = time()
            total = t1 - t0
            self.log.debug("Table deletion took: %.3fs", total)
        except ClientError as client_error:
            print("delete_table In ClientError block", client_error)
            error = client_error.response['Error']

        # except errorfactory.ResourceInUseException as error:
        #     import pdb
        #     print("delete_table In ResourceInUseException block", error)
        #     pdb.set_trace()
        #     print("bb")
        #     pass
        # except Exception as errorMessage:
        #     import pdb
        #     print("delete_table In Exception block", errorMessage)
        #     pdb.set_trace()


########################################
# UserCredentialRepository

class UserCredentialRepository(BaseDynamoDbRepository):
    """DynamoDb repository for UserCredential

    What should this repository be able to do:
        (CRUD)

        1. __get_field_value
        1. create_table_if_not_exists

        1. get_record_list
        1. get_record

        1. get_record_list
        1. find_record
        1. put_record
        1. delete_record

    Code Review:

        1. Review logging statements

    """

    def __init__(self, client=None):
        super().__init__('user_credential', client)
        self.PasswordUtility = PasswordUtility()

    # def __get_salt(self):
    #     import string
    #     import secrets
    #     alphabet = string.ascii_letters + string.digits
    #     password = ''.join(secrets.choice(alphabet) for i in range(8))

    def create_table_if_not_exists(self):
        t0 = time()
        try:
            if self.table_in_use():
                self.log.warning(f'Table {self.TABLE_NAME} is in use.')
                return
            response = self.client.create_table(
                TableName=self.TABLE_NAME,
                AttributeDefinitions=[
                    {"AttributeName": "username", "AttributeType": "S"}
                ],
                KeySchema=[
                    {"AttributeName": "username", "KeyType": "HASH"}
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1
                }
            )
            # Table creation is not instantaneous.
            # So by default, the table status would have been 'CREATING'.
            # When the table is created, table status would be 'ACTIVE'.
            # There is no await, so we use a waiter
            table_description = response['TableDescription']
            table_status = table_description['TableStatus']
            if table_status == 'CREATING':
                self.wait_for_table_exists()
            t1 = time()
            total = t1 - t0
            self.log.info("Table creation took: %.3fs", total)
        except ClientError as client_error:
            self.log.warning('Error creating table %s: %s', self.TABLE_NAME, client_error)

        # except Exception as error:
        #     import pdb
        #     print("In Exception block", error)
        #     pdb.set_trace()
        # except errorfactory.ResourceInUseException as error:
        #     import pdb
        #     print("In ResourceInUseException block", error)
        #     pdb.set_trace()
        #     print("bb")
        #     pass

    def get_field_value(self, key, value):
        value_tuple = value.popitem()  # value tuple consists of a type-value like: { 'S': 'SomeValue' }
        if value_tuple[0] == 'N':
            return float(value_tuple[1])
        if value_tuple[0] == 'S':
            return value_tuple[1]
        return value_tuple[1]

    def get_record_list(self) -> list:
        response = self.client.scan(TableName=self.TABLE_NAME)
        if 'Items' in response:
            response_items = response['Items']
            return list(
                map(lambda item:
                    {key: self.get_field_value(key, value) for key, value in item.items()},
                    response_items)
            )
        return []

    def get_record(self, partition_key: str) -> UserCredentialRecord|None:
        response = self.client.get_item(
            TableName=self.TABLE_NAME,
            Key={'username': {'S': partition_key}}
        )
        if 'Item' in response:
            return UserCredentialRecord(response['Item'])
        self.log.warning('Record does not exists')
        return None

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

    # def __get_salt_bytes(self, length=32):
    #     import secrets
    #     return secrets.token_bytes(length)

    # def hash_password(self, password_text, salt_bytes = None):
    #     import hashlib
    #     import base64
    #     if salt_bytes is None:
    #         salt_bytes = self.__get_salt_bytes()
    #     password_bytes = password_text.encode('utf-8')
    #     combined_bytes = salt_bytes + password_bytes
    #     sha256 = hashlib.sha256()
    #     sha256.update(combined_bytes)
    #     return (sha256.hexdigest(), base64.b64encode(salt_bytes).decode())

    def add_new_record(self, message: CreateUserCredentialMessage):
        insert_user_credential_record = InsertUserCredentialRecord(
            message).to_dynamodb_item()  # Transform message into record
        response = self.client.put_item(
            TableName=self.TABLE_NAME,
            Item=insert_user_credential_record,
            ReturnConsumedCapacity='TOTAL',
        )
        if 'Item' in response:
            return response['Item']
        self.log.debug(response)

    def update_password(self, message: UserCredentialPasswordUpdateMessage):
        update_record = UpdateUserCredentialPasswordRecord(message)
        response = self.client.update_item(
            TableName=self.TABLE_NAME,
            Key={
                'username': {'S': update_record.username, }
            },
            UpdateExpression='SET #PH = :ph, #PS = :ps, #DT = :dt',
            ExpressionAttributeNames={
                '#PH': 'password_hash',
                '#PS': 'password_salt',
                '#DT': 'password_last_changed_datetime',
            },
            ExpressionAttributeValues={
                ':ph': {'S': update_record.password_hash},
                ':ps': {'S': update_record.password_salt},
                ':dt': {'S': update_record.password_last_changed_datetime},
            },
            ReturnConsumedCapacity='TOTAL',
        )
        print(response)

    # def hash_password(self, password_text, salt_bytes = None):
    #     import hashlib, base64
    #     if salt_bytes is None:
    #         salt_bytes = self.__get_salt_bytes()
    #     password_bytes = password_text.encode('utf-8')
    #     combined_bytes = salt_bytes + password_bytes
    #     sha256 = hashlib.sha256()
    #     sha256.update(combined_bytes)
    #     return (sha256.hexdigest(), base64.b64encode(salt_bytes).decode())

    def validate_login(self, message: LoginMessage):
        #update_record = UpdateUserCredentialPasswordRecord(message)
        failed_login_attempts_tolerance = 6

        user_credential_record = self.get_record(message.username)
        print('user_credential_record', user_credential_record)

        failed_login_attempts = user_credential_record['failed_login_attempts']['N']
        if failed_login_attempts > failed_login_attempts_tolerance:
            print('failed_login_attempts', failed_login_attempts)
            return False

        salt_str = user_credential_record['password_salt']['S']
        password_hash = user_credential_record['password_hash']['S']

        salt_bytes = self.PasswordUtility.decode_base64_to_bytes(salt_str)
        (sha256_hex, salt_b64) = self.PasswordUtility.hash_password(message.password, salt_bytes)
        print('sha256_hex', sha256_hex)

        if password_hash == sha256_hex:
            print('Password: Valid')
            self.update_login_success_stats(message.username)
            return True
        else:
            print('Password: INVALID')
            self.update_login_fail_stats(message.username)
            return False

        # Update
        # last_login_attempt_datetime
        # last_successful_login
        # failed_login_attempts
        # last_login_attempt_datetime = user_credential_record['last_login_attempt_datetime']['S']
        # last_successful_login = user_credential_record['last_successful_login']['S']
        # failed_login_attempts = user_credential_record['failed_login_attempts']['S']
        #
        # self.update_login(
        #     message.username,
        #     failed_login_attempts,
        #     last_successful_login,
        #     last_login_attempt_datetime
        # )
        #user_credential_record.b64decode()

    def update_login_success_stats(self, username: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        response = self.client.update_item(
            TableName=self.TABLE_NAME,
            Key={
                'username': {'S': username}
            },
            UpdateExpression='SET #J = :j, #K = :k, #L = :l',
            ExpressionAttributeNames={
                '#J': 'failed_login_attempts',
                '#K': 'last_successful_login',
                '#L': 'last_login_attempt_datetime'
            },
            ExpressionAttributeValues={
                ':j': {'N': '0'},
                ':k': {'S': timestamp},
                ':l': {'S': timestamp}
            },
            ReturnConsumedCapacity='TOTAL',
        )
        print(response)

    def update_login_fail_stats(self, username: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        response = self.client.update_item(
            TableName=self.TABLE_NAME,
            Key={
                'username': {'S': username}
            },
            UpdateExpression='SET #J = #J + :j, #K = :k',
            ExpressionAttributeNames={
                '#J': 'failed_login_attempts',
                '#K': 'last_login_attempt_datetime',
            },
            ExpressionAttributeValues={
                ':j': {'N': '1'},
                ':k': {'S': timestamp},
            },
            ReturnConsumedCapacity='TOTAL',
        )
        print(response)

    def update_login(self, username: str,
                     failed_login_attempts: int = 0,
                     last_successful_login: int = 0,
                     last_login_attempt_datetime: str = ''):
        response = self.client.update_item(
            TableName=self.TABLE_NAME,
            Key={
                'username': {'S': username}
            },
            UpdateExpression='SET #PH = #PH + :ph, #PS = :ps, #DT = :dt',
            ExpressionAttributeNames={
                '#PH': 'failed_login_attempts',
                '#PS': 'last_successful_login',
                '#DT': 'last_login_attempt_datetime',
            },
            ExpressionAttributeValues={
                ':ph': {'S': failed_login_attempts},
                ':ps': {'S': last_successful_login},
                ':dt': {'S': last_login_attempt_datetime},
            },
            ReturnConsumedCapacity='TOTAL',
        )
        print(response)

    # def resert_record(self, record: InsertUserCredentialRecord):
    #     # new_item = {
    #     #     'username': {
    #     #         'S': record['username'] if 'username' in record else ''},
    #     #     'password_hash': {
    #     #         'S': record['password_hash'] if 'password_hash' in record else ''},
    #     #     'password_salt': {
    #     #         'S': record['password_salt'] if 'password_salt' in record else ''},
    #     #     'password_last_changed_datetime': {
    #     #         'S': record['password_last_changed_datetime'] if 'password_last_changed_datetime' in record else ''},
    #     #     'last_successful_login': {
    #     #         'S': record['last_successful_login'] if 'last_successful_login' in record else ''},
    #     #     'last_login_attempt_datetime': {
    #     #         'S': record['last_login_attempt'] if 'last_login_attempt' in record else ''},
    #     #     'failed_login_attempts': {
    #     #         'N': record['failed_login_attempts'] if 'failed_login_attempts' in record else '0'},
    #     #     'status': {
    #     #         'S': record['status'] if 'status' in record else ''},
    #     # }
    #     new_item = {}
    #
    #     if 'username' in record:
    #         new_item['username'] = {'S': record['username']}
    #     if 'password' in record:
    #         (sha256_hex, salt_b64) = self.repo.hash_password(record['password'])
    #         new_item['password_hash'] = {'S': sha256_hex}
    #         new_item['password_salt'] = {'S': salt_b64}
    #         new_item['password_last_changed_datetime'] = {'S': datetime.now(timezone.utc).isoformat()}
    #
    #     # if 'last_successful_login' in record:
    #     #     new_item['last_successful_login'] = record['last_successful_login']
    #     # if 'last_login_attempt_datetime' in record: new_item['last_login_attempt_datetime'] = record['last_login_attempt_datetime']
    #     # if 'failed_login_attempts' in record:
    #     #     new_item['failed_login_attempts'] = record['failed_login_attempts']
    #     # if 'status' in record:
    #     #     new_item['status'] = record['status']
    #
    #     response = self.client.put_item(
    #         TableName=self.TABLE_NAME,
    #         Item={
    #             'username': {
    #                 'S': record['username'] if 'username' in record else ''},
    #             'password_hash': {
    #                 'S': record['password_hash'] if 'password_hash' in record else ''},
    #             'password_salt': {
    #                 'S': record['password_salt'] if 'password_salt' in record else ''},
    #             'password_last_changed_datetime': {
    #                 'S': record[
    #                     'password_last_changed_datetime'] if 'password_last_changed_datetime' in record else ''},
    #             'last_successful_login': {
    #                 'S': record['last_successful_login'] if 'last_successful_login' in record else ''},
    #             'last_login_attempt_datetime': {
    #                 'S': record['last_login_attempt'] if 'last_login_attempt' in record else ''},
    #             'failed_login_attempts': {
    #                 'N': record['failed_login_attempts'] if 'failed_login_attempts' in record else '0'},
    #             # 'status': {
    #             #     'S': record['status'] if 'status' in record else 'NA'},
    #         },
    #         ReturnConsumedCapacity='TOTAL',
    #     )
    #     if 'Item' in response:
    #         return response['Item']
    #     self.log.debug(response)

    def delete_record(self, username):
        response = self.client.delete_item(
            TableName=self.TABLE_NAME,
            Key={'username': {'S': username}},
        )
        response_metadata = response['ResponseMetadata']
        http_status_code = response_metadata['HTTPStatusCode']
        if http_status_code != 200:
            self.log.debug(response)


########################################
# main

if __name__ == '__main__':  # pragma: no cover
    repo = BaseDynamoDbRepository('text_example')
    table_list = repo.wait_for_table_exists(1, 2)
