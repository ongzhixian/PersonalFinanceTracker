import json
import boto3
from botocore.exceptions import ClientError
import pdb

from example_common_aws import setup_aws_profile

setup_aws_profile()
sns_client = boto3.client('sns')

def publish_message(topic_arn, message):
    response = sns_client.publish(TopicArn=topic_arn, Message=message)
    return response['MessageId'] if 'MessageId' in response else None


def main():
    target_topic_arn = 'arn:aws:sns:us-east-1:009167579319:example-topic'
    message_id = publish_message(target_topic_arn, 'Some sample message 1')
    print('Message ID', message_id)

if __name__ == '__main__':
    main()
