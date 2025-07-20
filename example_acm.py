from os import environ
from zoneinfo import ZoneInfo, reset_tzpath
import boto3
from botocore.exceptions import ClientError

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
if runtime_dns_domain == 'AD.MLP.COM': reset_tzpath(['C:/Anaconda3/share/zoneinfo'])

boto3.setup_default_session(profile_name=aws_profile)
acm_client = boto3.client('acm')

boto3.setup_default_session(profile_name=aws_profile)

# s3 = boto3.resource('s3')
# s3_client = boto3.client('s3')

# def list_buckets():
#     for bucket in s3.buckets.all():
#         print(bucket.name)

def main():
    certs = acm_client.list_certificates()
    print("Certificates:", certs)


if __name__ == '__main__':
    main()
