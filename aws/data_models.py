########################################
# Imports

import logging
import boto3
#from botocore.exceptions import ClientError

########################################
# BaseDynamoDbModel

class BaseDynamoDbModel(object):
    """Base repository class for DynamoDb

    Use this base class to model business models based on DynamoDb.

    Code Review:

        1. Maybe move this to data_models.py

    """

    def __init__(self, client=None):
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

from message_types import (CreateUserCredentialMessage,
                           UserCredentialPasswordUpdateMessage,
                           LoginMessage)

from data_repositories import UserCredentialRepository


# UserCredential Business Logic

class UserCredential(BaseDynamoDbModel):
    """
    UserCredential business model

    Use this model to:

    1. get_user_credential_list(self) -> list
        Get a list of user credential objects

    2. get_user_credential(self, username:str) -> object
        Get user credential matching specified username

    3. add_user_credential(self, message:CreateUserCredentialMessage):
        Add user credential given CreateUserCredentialMessage

    4. update_user_credential_password(self, message:UserCredentialPasswordUpdateMessage)
        Updates the password of user credential given UserCredentialPasswordUpdateMessage

    5. remove_user_credential(self, username:str)
        Removes user credential object for specified username

    6. is_valid_login(self, message:LoginMessage)
        Validates if a LoginMessage contains valid credentials
    """

    def __init__(self):
        super().__init__()
        self.user_credential_repo = UserCredentialRepository(self.client)

    def get_user_credential_list(self) -> list:
        """
        Returns:
            list:
                A list of user credentials available in system.
        """
        return self.user_credential_repo.get_record_list()

    def get_user_credential(self, username: str) -> object:
        """
        Args:
            username (str):
                Username of user credential to return
        Returns:
            object:
                User credential record matching username
        """
        return self.user_credential_repo.get_record(username)

    def add_user_credential(self, message: CreateUserCredentialMessage):
        """
        Args:
            message (CreateUserCredentialMessage):
                Message containing parameters for creating user credential object
        Returns:
            None
        """
        return self.user_credential_repo.add_new_record(message)

    def update_user_credential_password(self, message: UserCredentialPasswordUpdateMessage):
        """
        Args:
            message (UserCredentialPasswordUpdateMessage):
                Message containing parameters to update password of specified user credential
        Returns:
            None
        """
        return self.user_credential_repo.update_password(message)

    def remove_user_credential(self, username: str):
        """
        Args:
            username(str):
                Username of user credential to remove
        Returns:
            None
        """
        return self.user_credential_repo.delete_record(username)

    def is_valid_login(self, message: LoginMessage):
        """
        Args:
            message (LoginMessage):
                Message containing the user credential to authenticate against system
        Returns:
            bool:
                True -> credentials in message match system
                False -> credentials in message does not match system
        """
        return self.user_credential_repo.validate_login(message)

    # def update_user_credential(self):
    #     """NOT IN USED -- too generic"""
    #     pass

#
# class Pft(BaseDynamoDbModel):
#     def __init__(self, owner:str):
#         super().__init__()
#         self.owner = owner
#         self.pft_account_repo = PftAccountRepository(self.client)
#         self.pft_account_history_repo = PftAccountHistoryRepository(self.client)
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