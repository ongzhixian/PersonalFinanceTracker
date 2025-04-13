import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='default')

dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')

def list_tables():
    response = client.list_tables()
    print(response['TableNames'])
    # for bucket in s3.buckets.all():
    #     print(bucket.name)

if __name__ == '__main__':
    list_tables()