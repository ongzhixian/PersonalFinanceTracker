import json
import boto3
from botocore.exceptions import ClientError
import pdb

from example_common_aws import setup_aws_profile, SqsClient

setup_aws_profile()
sqs_client = boto3.client('sqs')

# def publish_message(topic_arn, message):
#     response = sns_client.publish(TopicArn=topic_arn, Message=message)
#     return response['MessageId'] if 'MessageId' in response else None

class SqsClient(object):
    def __init__(self):
        self.client = boto3.client('sqs')

    def get_queue_list(self):
        try:
            response = self.client.list_queues()
            queues = response.get('QueueUrls', [])
            return queues
        except ClientError as e:
            print(f"Error listing queues: {e}")
            return []

    def create_queue(self, queue_name):
        try:
            print('\nCreating queue:', queue_name)
            response = self.client.create_queue(QueueName=queue_name)
            if 'QueueUrl' in response:
                return response['QueueUrl']
        except ClientError as e:
            print(f"Error creating queue: {e}")
            return None

    def delete_queue(self, queue_url):
        try:
            print('\nDeleting queue url:', queue_url)
            response = self.client.delete_queue(QueueUrl=queue_url)
            if 'ResponseMetadata' in response and response['ResponseMetadata'].get('HTTPStatusCode') == 200:
                return True
            return False
        except ClientError as e:
            print(f"Error deleting queue: {e}")
            return None
        
    def publish_message(self, queue_url, message):
        try:
            response = self.client.send_message(
                QueueUrl=queue_url,
                MessageBody=message,
                MessageAttributes={
                    'UpdateType': {
                        'DataType': 'String',
                        'StringValue': 'APPEND'
                    }
                }
            )
            return response['MessageId'] if 'MessageId' in response else None
        except ClientError as e:
            print(f"Error sending message: {e}")
            return None 

    def receive_and_delete_message(self, queue_url):
        # Receive message from SQS queue
        response = self.client.receive_message(QueueUrl=queue_url, MessageAttributeNames=['UpdateType'])
        print(response)

        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        # Delete received message from queue
        self.client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % message)

def main():
    sqs_client = SqsClient()
    queue_name = 'example-queue'
    
    # created_queue_url = sqs_client.create_queue(queue_name)
    # print('Created Queue URL:', created_queue_url)

    # all_queues = sqs_client.get_queue_list()
    # print('All Queues:', all_queues)
    # for queue in all_queues:
    #     print('Queue URL:', queue)

    msg_id = sqs_client.publish_message('https://sqs.us-east-1.amazonaws.com/009167579319/example-queue', 'Hello, this is a test message!')
    print('Message ID:', msg_id)

    # Delete the created queue
    # if created_queue_url:
    #     is_deleted = sqs_client.delete_queue(created_queue_url)
    #     print('Deleted Queue:', is_deleted)
    # message_id = publish_message(target_topic_arn, 'Some sample message 1')
    # print('Message ID', message_id)

if __name__ == '__main__':
    main()
