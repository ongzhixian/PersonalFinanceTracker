# import boto3
# from botocore.exceptions import ClientError
#
# boto3.setup_default_session(profile_name='default')
# s3 = boto3.resource('s3')
# s3_client = boto3.client('s3')
#
#
# def list_buckets():
#     for bucket in s3.buckets.all():
#         print(bucket.name)
#
#
# if __name__ == '__main__':
#     list_buckets()

class Praxis_CloudFront():
    def __init__(self):
        pass

    def demo(self):
        print(__name__, "OK")