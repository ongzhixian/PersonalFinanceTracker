import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='default')
cloudfront_client = boto3.client('cloudfront')


def display_distribution_list():
    distributions = cloudfront_client.list_distributions()
    print("CloudFront distributions:\n")
    print(distributions)

def main():
    pass

if __name__ == '__main__':
    main()
    