import json
import boto3
from botocore.exceptions import ClientError
import pdb

boto3.setup_default_session(profile_name='default')
client = boto3.client('sns')

def create_topic(topic_name):
    response = client.create_topic(Name=topic_name)
    print(response)

def delete_topic(topic_arn):
    response = client.delete_topic(TopicArn=topic_arn)
    print(response)

def publish_message(topic_arn, message):
    response = client.publish(
        TopicArn=topic_arn,
        Message=message,
    )
    print(response)

if __name__ == '__main__':
    #create_topic('sqs-error')
    # delete_topic('arn:aws:sns:us-east-1:009167579319:sqs-error')
    #delete_topic('arn:aws:sns:us-east-1:009167579319:hci-blazer-google-sheet-update-error')
    topic_arn = 'arn:aws:sns:us-east-1:009167579319:hci-blazer-google-sheet-update-sqs-error'
    publish_message(topic_arn, 'Some error message 1')