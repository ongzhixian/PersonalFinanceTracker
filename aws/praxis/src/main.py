import json
import os

import boto3

from praxis.aws import Praxis_S3

def get_provision_configuration():
    print(os.getcwd())
    print(__file__)
    # with open('./provision-configuration.json', 'r', encoding='utf8') as input_file:
    #     return json.load(input_file)

def setup_boto3():
    boto3.setup_default_session(profile_name='praxis')

def main():
    """Main function to run the application."""
    setup_boto3()
    # provision_configuration = get_provision_configuration()
    # print(provision_configuration)

    s3 = Praxis_S3()
    s3.list_buckets()

    return 0

if __name__ == "__main__":
    main()