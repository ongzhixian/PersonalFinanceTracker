"""Integration Tests for data_models

This is an integration test suite.

1. TestBaseDynamoDbModel
1. TestUserCredential

Run:

python -m unittest test_module.TestClass.test_method
"""

import unittest
from data_models import (UserCredential, CreateUserCredentialMessage,
                         UserCredentialPasswordUpdateMessage, LoginMessage)

class TestUserCredential(unittest.TestCase):

    def setUp(self):
        self.model = UserCredential()

    def test_get_user_credential_list(self):
        """
        python -m unittest test_data_models.TestUserCredential.test_get_user_credential_list
        """
        user_credential_list = self.model.get_user_credential_list()
        print(user_credential_list)
        self.assertIsInstance(user_credential_list, list)

    def test_get_user_credential(self):
        """
        python -m unittest test_data_models.TestUserCredential.test_get_user_credential
        """
        user_credential = self.model.get_user_credential('igruser')
        print('test_get_user_credential-user_credential', user_credential)
        self.assertIsInstance(user_credential, object)

    def test_add_user_credential(self):
        """
        python -m unittest test_data_models.TestUserCredential.test_add_user_credential
        """
        message = CreateUserCredentialMessage('igruser', 'igruser-password')
        self.model.add_user_credential(message)

    def test_update_user_credential_status(self):
        """
        We should be thinking operations and how they affected fields (instead of a generic update)
        A generic update implies that the operation is a complete replacement of existing.
        So this method `update_user_credential` is not a good one.
        Operations            -- Affected fields
        1. change password    -- (affects: password_hash, password_salt, password_last_changed_datetime)
        2. login              -- (affects: last_successful_login, last_login_attempt_datetime, failed_login_attempts, status
        So from the above, we now have 2 more messages:
        UserCredentialPasswordUpdateMessage
        LoginMessage
        """
        #message = UpdateUserCredentialMessage()
        user_credential = self.model.get_user_credential('igruser')
        self.model.update_user_credential()

    def test_update_user_credential_password(self):
        message = UserCredentialPasswordUpdateMessage('igruser', 'igruser-password')
        self.model.update_user_credential_password(message)

    def test_is_valid_login(self):
        message = LoginMessage('igruser', 'igruser-password')
        self.model.is_valid_login(message)


    def test_remove_user_credential(self):
        self.model.remove_user_credential('igruser')

    def test_print_UserCredentialRecord(self):
        from record_types import UserCredentialRecord
        record = UserCredentialRecord()
        print(record)



class TestLogin(unittest.TestCase):
    def setUp(self):
        self.model = UserCredential()

