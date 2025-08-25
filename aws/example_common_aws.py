import boto3
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath
from botocore.exceptions import ClientError
import pdb

def setup_aws_profile():
    mlp_domain = 'AD.MLP.COM'
    runtime_dns_domain = environ.get('USERDNSDOMAIN')
    aws_profile = 'stub-dev' if runtime_dns_domain == mlp_domain else None
    if runtime_dns_domain == mlp_domain: reset_tzpath(['C:/Anaconda3/share/zoneinfo'])
    print('Using %s for AWS profile' % aws_profile)
    boto3.setup_default_session(profile_name=aws_profile)

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


class SimpleQueue(object):
    def __init__(self, queue_url:str):
        self.client = boto3.client('sqs')
        self.queue_url = queue_url

    def enqueue(self, message):
        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message
        )
        return response.get('MessageId')

    def dequeue(self):
        response = self.client.receive_message(QueueUrl=self.queue_url, MaxNumberOfMessages=1)
        messages = response.get('Messages', [])
        if len(messages) == 0:
            print('No messages to dequeue.')
            return None
        # print(response)
        message = messages[0]
        receipt_handle = message['ReceiptHandle']

        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
        return message
        

class SimpleQueueService(object):
    def __init__(self):
        self.client = boto3.client('sqs')
        self.queue_dict = {}

    def get_queue(self, queue_name:str, use_cache:bool=True) -> SimpleQueue:
        """
        Returns a SimpleQueue object for the specified queue URL.
        If the queue URL is not found, returns None.
        """
        queue_url = self.get_queue_url(queue_name=queue_name, use_cache=use_cache)
        if queue_url is None:
            print(f"Queue '{queue_name}' not found.")
            return None
        return SimpleQueue(queue_url)

    def get_queue_name_list(self, use_cache=True):
        """
        Returns a list of queue names.
        If use_cache is True and the cache is populated, returns cached names.
        Otherwise, fetches from AWS and updates the cache.
        """
        if use_cache and self.queue_dict:
            return list(self.queue_dict.keys())
        try:
            self._refresh_queue_cache()
            return list(self.queue_dict.keys())
        except ClientError as e:
            print(f"Error listing queues: {e}")
            return []
        
    def get_queue_url_list(self, use_cache=True):
        """
        Returns a list of queue URLs.
        If use_cache is True and the cache is populated, returns cached URLs.
        Otherwise, fetches from AWS and updates the cache.
        """
        if use_cache and self.queue_dict:
            return list(self.queue_dict.values())
        try:
            self._refresh_queue_cache()
            return list(self.queue_dict.values())
        except ClientError as e:
            print(f"Error listing queues: {e}")
            return []

    def _refresh_queue_cache(self):
        """
        Fetches the list of queues from AWS and updates the internal cache.
        """
        response = self.client.list_queues()
        queues = response.get('QueueUrls', [])
        self.queue_dict = dict(sorted(
            ((url.rsplit('/', 1)[-1], url) for url in queues),
            key=lambda item: item[0]
        ))
        
    def get_queue_url(self, queue_name:str, use_cache:bool=True):
        """
        Returns the URL of the specified SQS queue.
        If use_cache is True and the cache is populated, returns cached URL.
        Otherwise, fetches from AWS and updates the cache.
        """
        if use_cache and self.queue_dict:
            return self.queue_dict.get(queue_name)
        try:
            self._refresh_queue_cache()
            return self.queue_dict.get(queue_name)
        except ClientError as e:
            print(f"Error getting queue: {e}")
            return None

    # def get_queue_list(self):
    #     return self.sqs_client.get_queue_list()
    # def create_queue(self, queue_name):
    #     return self.sqs_client.create_queue(queue_name)
    # def delete_queue(self, queue_url):
    #     return self.sqs_client.delete_queue(queue_url)
    # def publish_message(self, queue_url, message):
    #     return self.sqs_client.publish_message(queue_url, message)
    # def receive_and_delete_message(self, queue_url):
    #     return self.sqs_client.receive_and_delete_message(queue_url)