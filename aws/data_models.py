########################################
# Imports

import logging
import boto3
from botocore.exceptions import ClientError

from message_types import Message
from record_types import Record

########################################
# BaseDynamoDbRepository

########################################
# BaseDynamoDbModel

class BaseDynamoDbModel(object):
    """Base repository class for DynamoDb

    Use this base class to model business models based on DynamoDb.

    Code Review:

        1. Maybe move this to data_models.py

    """
    def __init__(self, client = None):
        self.client = boto3.client('dynamodb') if client is None else client
        self.__setup_logging(logging.DEBUG)

    def __setup_logging(self, logging_level):
        ch = logging.StreamHandler()
        ch.setLevel(logging_level)
        ch.setFormatter(logging.Formatter('[%(levelname).3s] %(asctime)s %(name)s - %(message)s'))
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(ch)
        self.log.setLevel(logging_level)

########################################
# UserCredential

from data_repositories import UserCredentialRepository

# UserCredential Messages

class CreateUserCredentialMessage(Message):
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password

class InsertUserCredentialRecord(Record):
    def __init__(self, message:CreateUserCredentialMessage):
        self.username = message.username
        self.password = message.password


# UserCredential Business Logic

class UserCredential(BaseDynamoDbModel):
    def __init__(self):
        super().__init__()
        self.user_credential_repo  = UserCredentialRepository(self.client)

    def get_user_credential_list(self) -> list:
        return self.user_credential_repo.get_record_list()

    def get_user_credential(self, username:str) -> object:
        return self.user_credential_repo.get_record(username)

    def add_user_credential(self, record:CreateUserCredentialMessage):
        # Transform message into record

        #return self.user_credential_repo.resert_record(record)
        pass

    def update_user_credential(self):
        pass

    def remove_user_credential(self):
        pass


#
# class Pft(BaseDynamoDbModel):
#     def __init__(self, owner:str):
#         super().__init__()
#         self.owner = owner
#         self.pft_account_repo = PftAccountRespository(self.client)
#         self.pft_account_history_repo = PftAccountHistoryRespository(self.client)
#
#     def add_account(self, account_name:str):
#         self.pft_account_repo.put_record({
#             'username': self.owner,
#             'name': account_name
#         })
#
#     def get_account_list(self):
#         # self.pft_account_repo.delete_record('zhixian', 'acctA1')
#         # self.pft_account_repo.delete_record('zhixian', 'acctA2')
#         return self.pft_account_repo.get_record_list_owned_by(self.owner)
#
#     def update_account(self, account_name:str, amount:float):
#         self.pft_account_history_repo.update_account(self.owner, account_name, amount)
#
#     def get_account_history(self, account_name:str):
#         # self.pft_account_repo.delete_record('zhixian', 'acct1')
#         # self.pft_account_repo.delete_record('zhixian', 'acct2')
#         # self.pft_account_repo.delete_record('zhixian', 'acct3')
#         self.pft_account_repo.delete_record('zhixian', 'acctA1')
#         self.pft_account_repo.delete_record('zhixian', 'acctA2')
#         account_list = self.get_account_list()
#
#
#         #
#         # account_id = ''
#         # self.pft_account_history_repo.get_record_list_owned_by(account_id)