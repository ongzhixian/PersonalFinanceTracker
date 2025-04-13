import unittest

from explore import dump_event_context

class Test_dump_event_context(unittest.TestCase):

    def test_when_dummy_data_return_ok_response(self):
        response = dump_event_context(None, None)
        self.assertEquals(response['statusCode'], 200)

if __name__ == '__main__':
    unittest.main()