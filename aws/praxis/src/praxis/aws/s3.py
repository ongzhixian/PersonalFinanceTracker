import boto3
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

class Praxis_S3():
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')

    def list_buckets(self):
        for bucket in self.s3.buckets.all():
            print(bucket.name)

    def demo(self):
        print(__name__, "OK")

def main():
    boto3.setup_default_session(profile_name='default')
    s3 = Praxis_S3()
    s3.list_buckets()

if __name__ == '__main__':
    main()