"""Integration Tests for ucm/user-credential endpoint
FILENAME: test_ucm_user_credential.py

This is an integration test suite.

"""
import unittest
import requests
import pdb  # pragma: no cover

class TestUcmUserCredential(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Get authentication ticket suitable for running tests.
        Instead of getting for each test, we get it once for the class.
        """
        cls.headers = {
            'Content-type': 'application/json; charset=utf-8'
        }
        response = requests.post("https://7pps9elf11.execute-api.us-east-1.amazonaws.com/authentication-ticket", 
            headers=cls.headers,
            json={"username": "testuser1", "password": "testuser1a"})
        if not response.ok:
            print("Failed to get authentication ticket:", response_json)
            raise Exception("Authentication failed")
        
        print("Authentication ticket retrieved successfully.")
        
        response_json = response.json()
        if 'data_object' not in response_json or 'token' not in response_json['data_object']:
            print("Invalid response structure:", response_json)
            raise Exception("Invalid response from authentication service")
        
        token = response_json['data_object']['token']
        cls.headers['Authorization'] = f'TOKEN {token}'
        cls.channel_id_map = {
            'zx-alerts': '-1002841796915',
        }


    def test_get_user_credential_list(self):
        """
        Test getting user credential list.
        """
        response = requests.get("https://7pps9elf11.execute-api.us-east-1.amazonaws.com/user-credential", 
            headers=self.headers)
        self.assertTrue(response.ok)
        if response.ok:
            print(response)
            print(response.json())

        

    def test_tuple(self):
        custom_dict = {
            'page_number': 1,
            'page_size': 5
        }
        (page_number, page_size) = tuple(custom_dict.items())
        print('page_number', page_number)
        print('page_size', page_size)
        


    # def test_invalid_channel_id_then_bad_request(self):
    #     """
    #     Test sending a simple notification.
    #     """
    #     invalid_channel_id = "-1002841796915999"
    #     response = requests.post("https://7pps9elf11.execute-api.us-east-1.amazonaws.com/notification", 
    #                              auth=("api", 'INLINE'),
    #                              headers=self.headers,
    #                              json={"chatId": invalid_channel_id, "message": "Test job complete."})
    #     self.assertTrue(response.status_code == 400)

if __name__ == '__main__': # pragma: no cover
    unittest.main()
