"""
Sections:
    Base message queue classes
        HciMessageQueue
"""

import boto3

from shared_message_queues import MessageQueue

class HciMessageQueue(MessageQueue):
    def __init__(self):
        self.sqs_client = boto3.client('sqs')
        self.hci_blazer_google_sheet_update_queue_name = 'hci-blazer-google-sheet-update'
        self.hci_blazer_google_sheet_update_queue_url = \
            f'https://sqs.us-east-1.amazonaws.com/009167579319/{self.hci_blazer_google_sheet_update_queue_name}'

    def enqueue_hci_blazer_google_sheet_update_message(self, update_type, json_message):
        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.hci_blazer_google_sheet_update_queue_url,
                MessageBody=json_message,
                MessageAttributes={
                    'UpdateType': {
                        'DataType': 'String',
                        'StringValue': update_type
                    }
                }
            )
            print(response)
        except Exception as error:
            print(error)