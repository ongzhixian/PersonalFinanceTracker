import json
import boto3
from botocore.exceptions import ClientError
import pdb

from example_common_aws import setup_aws_profile, SqsClient, SimpleQueueService

setup_aws_profile()
sqs_client = boto3.client('sqs')

# def publish_message(topic_arn, message):
#     response = sns_client.publish(TopicArn=topic_arn, Message=message)
#     return response['MessageId'] if 'MessageId' in response else None

def main():
    sqs = SimpleQueueService()
    # for queue_url in sqs.get_queue_url_list():
    #     print('Queue URL:', queue_url)
    # for queue_name in sqs.get_queue_name_list():
    #     print('Queue Name:', queue_name)
    # queue_url = sqs.get_queue_url('example-queue')
    # print('Specific Queue URL:', queue_url)
    example_queue = sqs.get_queue('example-queue')
    example_queue.enqueue("Enqueued message 3")
    dequeued_message = example_queue.dequeue()
    print('Dequeued Message:', dequeued_message)


def main2():
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
