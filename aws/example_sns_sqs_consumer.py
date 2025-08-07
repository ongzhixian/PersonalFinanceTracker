import boto3
import json
import time
from botocore.exceptions import ClientError

from example_common_aws import setup_aws_profile

setup_aws_profile()
sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')

def create_sqs_queue_for_sns(queue_name):
    """Create an SQS queue that can receive SNS messages"""
    try:
        # Create SQS queue
        response = sqs_client.create_queue(QueueName=queue_name)
        queue_url = response['QueueUrl']
        
        # Get queue attributes including ARN
        queue_attrs = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['QueueArn']
        )
        queue_arn = queue_attrs['Attributes']['QueueArn']
        
        print(f"Created SQS queue: {queue_name}")
        print(f"Queue URL: {queue_url}")
        print(f"Queue ARN: {queue_arn}")
        
        return queue_url, queue_arn
    except ClientError as e:
        print(f"Error creating queue: {e}")
        return None, None

def subscribe_sqs_to_sns(topic_arn, queue_arn):
    """Subscribe an SQS queue to an SNS topic"""
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='sqs',
            Endpoint=queue_arn
        )
        subscription_arn = response.get('SubscriptionArn')
        print(f"Subscribed SQS queue to SNS topic")
        print(f"Subscription ARN: {subscription_arn}")
        return subscription_arn
    except ClientError as e:
        print(f"Error subscribing to SNS: {e}")
        return None

def consume_messages_from_sqs(queue_url, max_messages=10):
    """Consume messages directly from SQS queue (no protocol needed here!)"""
    print(f"Starting to consume messages from SQS queue...")
    print("Press Ctrl+C to stop")
    
    message_count = 0
    try:
        while message_count < max_messages:
            # Poll for messages (this is direct consumption!)
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,  # Long polling
                VisibilityTimeoutSeconds=30
            )
            
            messages = response.get('Messages', [])
            
            if messages:
                for message in messages:
                    message_count += 1
                    print(f"\n--- Message {message_count} ---")
                    
                    # Parse SNS message (it's wrapped in JSON)
                    try:
                        sns_message = json.loads(message['Body'])
                        print(f"SNS Message: {sns_message.get('Message', 'No message content')}")
                        print(f"Subject: {sns_message.get('Subject', 'No subject')}")
                        print(f"Timestamp: {sns_message.get('Timestamp', 'No timestamp')}")
                    except json.JSONDecodeError:
                        print(f"Raw message: {message['Body']}")
                    
                    # Delete message after processing
                    sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    print("Message processed and deleted")
                    
                    if message_count >= max_messages:
                        break
            else:
                print("No messages available, waiting...")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\nStopping message consumption...")
    
    print(f"Consumed {message_count} messages total")

def main():
    topic_arn = 'arn:aws:sns:us-east-1:009167579319:example-topic'
    queue_name = 'example-sns-consumer-queue'
    
    print("Setting up SQS queue for direct message consumption...")
    
    # Step 1: Create SQS queue
    queue_url, queue_arn = create_sqs_queue_for_sns(queue_name)
    if not queue_url:
        print("Failed to create SQS queue")
        return
    
    # Step 2: Subscribe SQS queue to SNS topic
    subscription_arn = subscribe_sqs_to_sns(topic_arn, queue_arn)
    if not subscription_arn:
        print("Failed to subscribe to SNS topic")
        return
    
    print("\nSetup complete! Now you can consume messages directly from SQS...")
    print("(Send some messages to the SNS topic from another script)")
    
    # Step 3: Consume messages directly (no protocol needed for this part!)
    consume_messages_from_sqs(queue_url)

if __name__ == '__main__':
    main()
