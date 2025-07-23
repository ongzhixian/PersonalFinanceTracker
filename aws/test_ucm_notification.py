"""Integration Tests for ucm/notification endpoint (shared_user_credential.py)
FILENAME: test_ucm_notification.py

This is an integration test suite.

"""
import unittest
import requests

class TestUcmNotification(unittest.TestCase):

    def setUp(self):
        self.headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Content-type': 'application/json; charset=utf-8',
        }
        self.channel_id_map = {
            'zx-alerts': '-1002841796915',
        }

    def tearDown(self):
        pass

    def test_send_notification(self):
        """
        Test sending a simple notification.
        """
        channel_id = self.channel_id_map['zx-alerts']
        response = requests.post("https://7pps9elf11.execute-api.us-east-1.amazonaws.com/notification", 
            headers=self.headers,
            json={"chatId": channel_id, "message": "Test job complete."})
        self.assertTrue(response.ok)

    def test_invalid_channel_id_then_bad_request(self):
        """
        Test sending a simple notification.
        """
        invalid_channel_id = "-1002841796915999"
        response = requests.post("https://7pps9elf11.execute-api.us-east-1.amazonaws.com/notification", 
                                 auth=("api", 'INLINE'),
                                 headers=self.headers,
                                 json={"chatId": invalid_channel_id, "message": "Test job complete."})
        
        self.assertTrue(response.status_code == 400)

if __name__ == '__main__': # pragma: no cover
    unittest.main()
