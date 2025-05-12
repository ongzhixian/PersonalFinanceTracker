"""
Sections:
    Base Entity classes
        DynamoDbEntity
    Base Repository classes
        BaseRepositorya
"""

import boto3

class MessageQueue(object):
    pass

class HciMessageQueue(MessageQueue):
    def __init__(self):
        self.sqs_client = boto3.client('sqs')
        self.hci_blazer_google_sheet_update_queue_name = 'hci-blazer-google-sheet-update'
        self.hci_blazer_google_sheet_update_queue_url = \
            f'https://sqs.us-east-1.amazonaws.com/009167579319/{self.hci_blazer_google_sheet_update_queue_name}'

    def enqueue_hci_blazer_google_sheet_update_message(self, updateType, json_message):
        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.hci_blazer_google_sheet_update_queue_url,
                MessageBody=json_message,
                MessageAttributes={
                    'UpdateType': {
                        'DataType': 'String',
                        'StringValue': updateType
                    }
                }
            )
            print(response)
        except Exception as error:
            print(error)