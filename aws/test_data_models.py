"""Integration Tests for data_models

This is an integration test suite.

1. TestBaseDynamoDbModel
1. TestUserCredential

Run:

python -m unittest test_module.TestClass.test_method
"""

import unittest
from data_models import UserCredential, CreateUserCredentialMessage

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
        user_credential = self.model.get_user_credential('zhixian')
        print(user_credential)
        self.assertIsInstance(user_credential, object)

    def test_add_user_credential(self):
        """
        python -m unittest test_data_models.TestUserCredential.test_add_user_credential
        """
        message = CreateUserCredentialMessage('zhixian', 'zhixian-password')
        self.model.add_user_credential(message)

    def test_update_user_credential(self):
        self.model.update_user_credential()

    def test_remove_user_credential(self):
        self.model.remove_user_credential()
