"""Integration Tests for UserCredentialRepository (shared_user_credential.py)
FILENAME: test_shared_user_credential.py

This is an integration test suite.

"""
import unittest
from shared_user_credential import UserCredentialRepository
from shared_user_credential_messages import AddUserCredentialMessage, AuthenticateUserCredentialMessage, UpdateUserCredentialPasswordMessage

class TestUserCredentialRepository(unittest.TestCase):

    def setUp(self):
        self.user_credential_repository = UserCredentialRepository()

    def tearDown(self):
        pass
        # self.user_credential_repository.__remove_user_credential__('unittestuser')

    def test_add_user_credential(self):
        """
        Test adding a user credential.
        """
        message = AddUserCredentialMessage(
            username='unittestuser',
            password='unittestpassword'
        )
        result = self.user_credential_repository.add_user_credential(message)
        self.assertTrue(result)

    def test_get_user_credential(self):
        """
        Test adding a user credential.
        """
        result = self.user_credential_repository.get_user_credential('unittestuser')
        self.assertTrue(result)

    # # @unittest.skip("We do not want to test this by default")
    # def test_create_table_if_not_exists(self):
    #     # table_list = self.repo.get_table_list()
    #     # print('BEFORE', table_list)
    #     #
    #     # if self.repo.table_exists():
    #     #     self.repo.delete_table(self.repo.TABLE_NAME)
    #     self.repo.create_table_if_not_exists()
    #     table_list = self.repo.get_table_list()
    #     print('AFTER', table_list)
    #     pass
    #
    # @unittest.skip("We do not want to test this by default")
    # def test_get_record_list(self):
    #     record_list = self.repo.get_record_list()
    #     print(len(record_list))
    #
    # # def test_get_record
    #
    # # def test_find_record
    #
    # @unittest.skip("We do not want to test this by default")
    # def test_put_record(self):
    #     # insert else update
    #     # vice-versa -> update_if_exist or insert (upsert)
    #     # alt wording
    #     # insert else replace
    #     # replace or insert (resert)
    #     user_input = {
    #         'username': 'zhixian',
    #         'password': 'my secret password'
    #     }
    #
    #     self.repo.resert_record(record={
    #         'username': 'zhixian',
    #         'password': 'zhixian',
    #     })
    #     record_list = self.repo.get_record_list()
    #     print(record_list)
    #     # (sha256_hex, salt_b64) = self.repo.hash_password('my password')
    #     #
    #     # record = {
    #     #     'username': 'zhixian',
    #     #     'password': sha256_hex,
    #     # }
    #     #
    #     #
    #     # res = {
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
    #     # print(res)
    #
    # @unittest.skip("We do not want to test this by default")
    # def test_func(self):
    #     import secrets
    #     import hashlib
    #     import base64
    #     password_text = 'this is my password'
    #     salt_bytes = secrets.token_bytes()
    #     password_bytes = password_text.encode('utf-8')
    #     combined_bytes = salt_bytes + password_bytes
    #     sha256 = hashlib.sha256()
    #     sha256.update(combined_bytes)
    #     sha256.digest()
    #     print(sha256.hexdigest())
    #     print(salt_bytes)
    #     print(base64.b64encode(salt_bytes).decode())
    #
    # @unittest.skip("We do not want to test this by default")
    # def test__hash_password(self):
    #     password_text = 'my secret password'
    #     sha_digest1 = self.repo.hash_password(password_text)
    #
    #     print(sha_digest1[1])
    #     import base64
    #     sha_digest2 = self.repo.hash_password(password_text,
    #                                           base64.b64decode(sha_digest1[1])
    #                                           )
    #     print(sha_digest1)
    #     print(sha_digest2)


# class TestUserCredentialRepository(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here

if __name__ == '__main__': # pragma: no cover
    unittest.main()
