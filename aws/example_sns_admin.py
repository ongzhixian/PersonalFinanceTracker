import json
import boto3
from botocore.exceptions import ClientError
import pdb

from example_common_aws import setup_aws_profile

setup_aws_profile()

class SnsClient(object):
    def __init__(self):
        self.client = boto3.client('sns')
    
    def get_topic_list(self):
        try:
            response = self.client.list_topics()
            topics = [topic['TopicArn'] for topic in response.get('Topics', [])]
            return topics
        except ClientError as e:
            print(f"Error listing topics: {e}")
            return []
        
    def create_topic(self, topic_name):
        try:
            print('\nCreating topic:', topic_name)
            response = self.client.create_topic(Name=topic_name)
            if 'TopicArn' in response:
                return response['TopicArn']
        except ClientError as e:
            print(f"Error creating topic: {e}")
            return None
        
    def delete_topic(self, topic_arn):
        try:
            print('\nDeleting topic arn:', topic_arn)
            response = self.client.delete_topic(TopicArn=topic_arn)
            if 'ResponseMetadata' in response and response['ResponseMetadata'].get('HTTPStatusCode') == 200:
                return True
            return False
        except ClientError as e:
            print(f"Error deleting topic: {e}")
            return None

    def get_all_subscriptions(self):
        try:
            response = self.client.list_subscriptions()
            subscriptions = response.get('Subscriptions', [])
            print('Subscriptions:', response)
            print('Subscriptions count:', len(subscriptions))
            for sub in subscriptions:
                print(f"Subscription ARN: {sub['SubscriptionArn']}, Protocol: {sub['Protocol']}, Endpoint: {sub['Endpoint']}")
            subscriptions = [sub['SubscriptionArn'] for sub in response.get('Subscriptions', [])]
            return subscriptions
        except ClientError as e:
            print(f"Error listing subscriptions: {e}")
            return []

    def remove_all_subscriptions(self):
        subscriptions = self.get_all_subscriptions()
        for sub_arn in subscriptions:
            try:
                print(f"Unsubscribing: {sub_arn}")
                self.client.unsubscribe(SubscriptionArn=sub_arn)
            except ClientError as e:
                print(f"Error unsubscribing {sub_arn}: {e}")

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
            response = self.client.create_queue(QueueName=queue_name)
            return response['QueueUrl'] if 'QueueUrl' in response else None
        except ClientError as e:
            print(f"Error creating queue: {e}")
            return None

    def delete_queue(self, queue_url):
        try:
            response = self.client.delete_queue(QueueUrl=queue_url)
            if 'ResponseMetadata' in response and response['ResponseMetadata'].get('HTTPStatusCode') == 200:
                return True
            return False
        except ClientError as e:
            print(f"Error deleting queue: {e}")
            return None
        
    def get_queue_attributes(self, queue_url, attribute_names=['All']):
        """Get attributes of a specific queue"""
        try:
            response = self.client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=attribute_names
            )
            return response
            # return response['Attributes'] if 'Attributes' in response else {}
        except ClientError as e:
            print(f"Error getting queue attributes: {e}")
            return {}


# HELPER FUNCTIONS

def print_topic_list(topic_list):
    for index, topic_arn in enumerate(topic_list):
        print(f"{index}: {topic_arn}")

def print_queue_list(queue_list):
    for index, queue_url in enumerate(queue_list):
        print(f"{index}: {queue_url}")

# MAIN SCRIPTS

def main_sns(clean_up=False):
    print("Creating and listing SNS topics...")
    sns_client = SnsClient()
    

    print('\nInitial topics:')
    topic_list = sns_client.get_topic_list()
    print_topic_list(topic_list)
    
    topic_name = 'example-topic'

    topic_arn = sns_client.create_topic(topic_name)
    print(f"Created topic ARN: {topic_arn}")

    # topic should have subscribers
    # A common pattern is to create a topic, subscribe to it, and then publish messages using SQS
    # So create SQS queue and subscribe it to the topic
    if topic_arn:
        queue_name = f'{topic_name}-queue'
        sqs_client = SqsClient()
        queue_url = sqs_client.create_queue(queue_name)
        print(f"Created queue URL: {queue_url}")
        
        if queue_url:
            # Get the queue ARN
            queue_attrs = sqs_client.client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['QueueArn']
            )
            queue_arn = queue_attrs['Attributes']['QueueArn']

            # Create policy that allows SNS to send messages to this SQS queue
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowSNSToSendMessage",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "sns.amazonaws.com"
                        },
                        "Action": "sqs:SendMessage",
                        "Resource": queue_arn,
                        "Condition": {
                            "ArnEquals": {
                                "aws:SourceArn": topic_arn
                            }
                        }
                    }
                ]
            }

            # Replaces the default policy with the new one
            sqs_client.client.set_queue_attributes(
                QueueUrl=queue_url,
                Attributes={
                    'Policy': json.dumps(policy)
                }
            )
            
            # Subscribe the SQS queue to the SNS topic
            subscription_arn = sns_client.client.subscribe(
                TopicArn=topic_arn,
                Protocol='sqs',
                Endpoint=queue_arn
            )['SubscriptionArn']
            
            print(f"Subscribed SQS queue to SNS topic. Subscription ARN: {subscription_arn}")
        else:
            print("Failed to create SQS queue.")

    sub = sns_client.get_all_subscriptions()

    if clean_up:
        topic_deleted = sns_client.delete_topic(topic_arn)
        print('Topic is deleted:', topic_deleted)

        print('\nTopics after deletion:')
        topic_list = sns_client.get_topic_list()
        print_topic_list(topic_list)

        # sns_client.remove_all_subscriptions()
        # sub = sns_client.get_all_subscriptions()


def main_sqs(clean_up=False):
    print("Creating and listing SQS queues...")
    sqs_client = SqsClient()

    print('\nInitial queues:')
    queue_list = sqs_client.get_queue_list()
    print_queue_list(queue_list)

    # Error creating queue: An error occurred (AWS.SimpleQueueService.QueueDeletedRecently) when calling the CreateQueue operation: 
    # You must wait 60 seconds after deleting a queue before you can create another with the same name.
    
    queue_url = sqs_client.create_queue('example-queue')
    print(f"Created queue URL: {queue_url}")

    # print('\nQueues after creation:')
    # queue_list = sqs_client.get_queue_list()
    # print_queue_list(queue_list)

    if clean_up:
        queue_deleted = sqs_client.delete_queue(queue_url)
        print('Queue is deleted:', queue_deleted)

        print('\nQueues after deletion:')
        queue_list = sqs_client.get_queue_list()
        print_queue_list(queue_list)



if __name__ == '__main__':
    main_sns()
    # main_sqs()
