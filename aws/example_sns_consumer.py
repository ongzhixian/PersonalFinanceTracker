import time
import json
import boto3
from botocore.exceptions import ClientError
import pdb

from example_common_aws import setup_aws_profile

setup_aws_profile()
sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')

def check_queue_exists(queue_url):
    """Check if the SQS queue exists and get its attributes"""
    try:
        response = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All']
        )
        print("Queue exists and is accessible")
        print(f"Queue ARN: {response['Attributes'].get('QueueArn')}")
        print(f"Messages Available: {response['Attributes'].get('ApproximateNumberOfMessages', 'Unknown')}")
        print(f"Messages In Flight: {response['Attributes'].get('ApproximateNumberOfMessagesNotVisible', 'Unknown')}")
        return True
    except ClientError as e:
        print(f"Queue check failed: {e}")
        return False

def consume_messages_from_sqs(queue_url, max_messages=10):
    """Consume messages directly from SQS queue (no protocol needed here!)"""
    print(f"Starting to consume messages from SQS queue...")
    print(f"Queue URL: {queue_url}")
    
    # First check if queue exists and is accessible
    if not check_queue_exists(queue_url):
        return
    
    print("Press Ctrl+C to stop")

    message_count = 0
    try:
        while message_count < max_messages:
            print(f"\nPolling for messages... (attempt {message_count + 1})")
            
            # Poll for messages (this is direct consumption!)
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,  # Long polling
                VisibilityTimeout=30
            )

            messages = response.get('Messages', [])

            if messages:
                print(f"Received {len(messages)} message(s)")
                for message in messages:
                    message_count += 1
                    print(f"\n--- Message {message_count} ---")

                    # Parse SNS message (it's wrapped in JSON)
                    try:
                        sns_message = json.loads(message['Body'])
                        print(f"SNS Message: {sns_message.get('Message', 'No message content')}")
                        print(f"Subject: {sns_message.get('Subject', 'No subject')}")
                        print(f"Timestamp: {sns_message.get('Timestamp', 'No timestamp')}")
                        print(f"Message ID: {sns_message.get('MessageId', 'No message ID')}")
                        
                        # Try to parse the inner message as JSON too
                        try:
                            inner_message = json.loads(sns_message.get('Message', '{}'))
                            print(f"Parsed inner message: {json.dumps(inner_message, indent=2)}")
                        except (json.JSONDecodeError, TypeError):
                            # Inner message is just text, not JSON
                            pass
                            
                    except json.JSONDecodeError:
                        print(f"Raw message (not SNS format): {message['Body']}")

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
    queue_url = 'https://sqs.us-east-1.amazonaws.com/009167579319/example-topic-queue'
    
    print("SNS-SQS Consumer")
    print("=" * 50)
    print("If no messages appear, make sure:")
    print("1. The SNS topic exists and you have publish permissions")
    print("2. The SQS queue exists and has proper SNS permissions")
    print("3. The SQS queue is subscribed to the SNS topic")
    print("4. Run setup_sns_sqs.py first if you haven't already")
    print("=" * 50)
    
    consume_messages_from_sqs(queue_url, max_messages=5)

if __name__ == '__main__':
    main()
