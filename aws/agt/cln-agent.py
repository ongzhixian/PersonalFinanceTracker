
import boto3
import threading
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentMessage:
    type: str = "string"
    message: str = ""

sqs = boto3.client('sqs')

def send_message(message, sqs, queue_url):
    queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'
    sqs.send_message(QueueUrl=queue_url, MessageBody='Hello from Agent A')

def process_message(message, sqs, queue_url):
    print(f"Received message: {message['Body']}")
    # Process the message here
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )


def receive_message_thread():
    queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'
    print("Listening for messages. Press Ctrl+C to stop.")
    threads = []
    try:
        while True:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=5,
                WaitTimeSeconds=10
            )
            if 'Messages' in response:
                for message in response['Messages']:
                    t = threading.Thread(target=process_message, args=(message, sqs, queue_url))
                    t.start()
                    threads.append(t)
                # Clean up finished threads to avoid memory leak
                threads = [th for th in threads if th.is_alive()]
            else:
                print("No messages received.")
    except KeyboardInterrupt:
        print("\nShutting down listener...")
        for t in threads:
            t.join()

if __name__ == "__main__":
    t = threading.Thread(target=receive_message_thread)
    t.start()
    t.join()