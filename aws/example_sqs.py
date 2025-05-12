import json
import boto3
from botocore.exceptions import ClientError
import pdb

boto3.setup_default_session(profile_name='default')
client = boto3.client('sqs')

def list_queues():
    response = client.list_queues()
    for queue_url in response['QueueUrls']:
        print(queue_url)
    # print(response['QueueUrls'])
    # print(response)
    # for bucket in s3.buckets.all():
    #     print(bucket.name)

def create_queue(queue_name):
    response = client.create_queue(QueueName=queue_name)
    print(response)

def delete_queue(queue_url):
    response = client.delete_queue(QueueUrl=queue_url)
    print(response)

def send_message(queue_url, message):
    try:
        response = client.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
            MessageAttributes={
                'UpdateType': {
                    'DataType': 'String',
                    'StringValue': 'APPEND'
                }
            }
        )
        print(response)
    except Exception as error:
        print(dir(error))
        print(type(error))
        print(error)


def receive_and_delete_message(queue_url):
    # Receive message from SQS queue
    response = client.receive_message(QueueUrl=queue_url, MessageAttributeNames=['UpdateType'])
    print(response)

    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % message)

if __name__ == '__main__':
    queue_name = 'hci-blazer-google-sheet-update'
    queue_url = f'https://sqs.us-east-1.amazonaws.com/009167579319/{queue_name}'
    #create_queue(queue_name)
    #delete_queue(queue_url)
    #list_queues()

    sample_data = json.dumps([
        ['item 3', 'Some student', '2025-05-10', '2025-05-24'],
        ['item 4', 'Some student', '2025-05-10', '2025-05-24']
    ])

    send_message(queue_url, sample_data)
    #receive_and_delete_message(queue_url)
