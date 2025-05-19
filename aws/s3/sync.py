"""Sync contents of a folder to S3 bucket
https://channaly.medium.com/how-to-host-static-website-with-https-using-amazon-s3-251434490c59
"""
import json
import os
import boto3
from botocore.exceptions import ClientError
import sys

boto3.setup_default_session(profile_name='stub-dev')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

target_directory = './hci-uat/'

def upload_to_s3(target_bucket, object_key, source_file_path):
    try:
        response = s3_client.upload_file(source_file_path, target_bucket, object_key)
        return response
    except ClientError as e:
        print(e)

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print('  Usage: python.exe .\sync.py <folder-path> <bucket-name>')
        print('Example: python.exe .\sync.py .\hci-uat\ "emptool-public"')
        exit(1)

    target_directory = sys.argv[1]
    target_bucket = sys.argv[2]
    print(f"Syncing {target_directory} to S3://{target_bucket}")
    config_key = f"{os.path.normpath(target_directory)}_to_{target_bucket}"
    #print('config_key', config_key)

    sync_json = {}
    with open('sync.json') as in_file:
        sync_json = json.load(in_file)

    latest_file = None
    latest_timestamp = None

    prev_stored_timestamp = None
    if config_key in sync_json:
        prev_stored_timestamp = sync_json[config_key]
        print('prev_stored_timestamp exists:', prev_stored_timestamp)

    target_directory_name = os.path.dirname(target_directory)
    for root, dirs, file_names in os.walk(target_directory):
        for file_name in file_names:
            src_path = os.path.join(root, file_name)
            dst_path = os.path.normpath(os.path.join(root.removeprefix(target_directory_name), file_name)).replace('\\','/').strip('/')

            timestamp = os.path.getmtime(src_path)
            if prev_stored_timestamp is None or timestamp > prev_stored_timestamp:
                print(f"Copy {src_path} to {dst_path}")
                #upload_to_s3('lab-bucket1', dst_path, src_path)
                upload_to_s3(target_bucket, dst_path, src_path)

            if latest_timestamp is None or timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_file = src_path

    print('Largest file timestamp:', latest_timestamp)
    # Store the largest timestamp and persist it to file
    sync_json[config_key] = latest_timestamp
    with open('sync.json', 'w', encoding='utf-8') as out_file:
        json.dump(sync_json, out_file, indent=4)
