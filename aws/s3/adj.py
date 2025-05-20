"""Script to fix (adjust) the content type of files in S3 bucket.
https://channaly.medium.com/how-to-host-static-website-with-https-using-amazon-s3-251434490c59
"""
import logging
import json
import os
import boto3
from botocore.exceptions import ClientError
import sys

logger = logging.getLogger()

boto3.setup_default_session(profile_name='stub-dev')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

target_directory = './hci-uat/'

def get_content_type(target_bucket, object_key) -> str|None:
    try:
        response = s3_client.head_object(Bucket=target_bucket, Key=object_key)
        if 'ContentType' in response:
            return response['ContentType']
        else:
            return None
    except ClientError as e:
        print(e)

def get_object_key_list(target_bucket) -> list:
    object_list = []
    try:
        list_objects_params = { 'Bucket': target_bucket }

        while True:
            response = s3_client.list_objects_v2(**list_objects_params)
            if 'Contents' in response:
                object_list.extend([s3_object['Key'] for s3_object in response['Contents']])

            if response['IsTruncated']:
                continuation_token = response['NextContinuationToken']
                list_objects_params['ContinuationToken'] = continuation_token
            else:
                break
    except ClientError as e:
        print(e)
    return object_list

def get_suggested_content_type(object_key):
    ext = os.path.splitext(object_key)[1].lower()
    # Based on https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types/Common_types
    match ext:
        case '.css':     return 'text/css'
        case '.csv':     return 'text/csv'
        case '.doc':     return 'application/msword'
        case '.docx':    return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        case '.gif':     return 'image/gif'
        case '.htm':     return 'text/html'
        case '.html':   return 'text/html'
        case '.ico':    return 'image/vnd.microsoft.icon'
        case '.jpeg':   return 'image/jpeg'
        case '.jpg':    return 'image/jpeg'
        case '.js':     return 'text/javascript'
        case '.json':   return 'application/json'
        case '.md':     return 'text/markdown'
        case '.png':    return 'image/png'
        case '.pdf':    return 'application/pdf'
        case '.ppt':    return 'application/vnd.ms-powerpoint'
        case '.pptx':   return 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        case '.svg':    return 'image/svg+xml'
        case '.xhtml':  return 'application/xhtml+xml'
        case '.xls':    return 'application/vnd.ms-excel'
        case '.xlsx':   return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        case '.xml':    return 'application/xml'
        case '.zip':    return 'application/zip'
        case _:
            logger.warning('USING DEFAULT')
            return 'binary/octet-stream' # Default in AWS

def fix_content_type(bucket_name, object_key, content_type):
    response = s3_client.copy_object(
        Bucket=bucket_name,
        CopySource={
            "Bucket": bucket_name,
            "Key": object_key
        },
        Key=object_key,
        ContentType=content_type,
        MetadataDirective='REPLACE',
    )


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print('  Usage: python.exe .\adj.py <folder-path> <bucket-name>')
        print('Example: python.exe .\adj.py .\hci-uat\ "emptool-public"')
        exit(1)

    target_directory = sys.argv[1]
    target_bucket = sys.argv[2]
    print(f"Syncing {target_directory} to S3://{target_bucket}")

    # Defines a config key for with configuration JSON file.
    config_key = f"{os.path.normpath(target_directory)}_to_{target_bucket}"

    # Get previously stored files max timestamp (if any)

    prev_stored_timestamp = None

    sync_json = {}
    with open('sync.json') as in_file:
        sync_json = json.load(in_file)

    if config_key in sync_json:
        prev_stored_timestamp = sync_json[config_key]
        print('prev_stored_timestamp exists:', prev_stored_timestamp)

    # Get list of objects in bucket
    # Iterate through the list of objects
    # And check the
    object_key_list = get_object_key_list(target_bucket)
    for object_key in object_key_list:
        content_type = get_content_type(target_bucket, object_key)
        suggested_content_type = get_suggested_content_type(object_key)
        print(f'object_key: {object_key}, content_type: {content_type}', 'suggested_content_type', suggested_content_type)
        if suggested_content_type != content_type:
            fix_content_type(target_bucket, object_key, suggested_content_type)


    # Origin
    #
    # latest_file = None
    # latest_timestamp = None
    #
    # target_directory_name = os.path.dirname(target_directory)
    # for root, dirs, file_names in os.walk(target_directory):
    #     for file_name in file_names:
    #         src_path = os.path.join(root, file_name)
    #         dst_path = os.path.normpath(os.path.join(root.removeprefix(target_directory_name), file_name)).replace('\\','/').strip('/')
    #
    #         timestamp = os.path.getmtime(src_path)
    #         if prev_stored_timestamp is None or timestamp > prev_stored_timestamp:
    #             print(f"Copy {src_path} to {dst_path}")
    #             #upload_to_s3('lab-bucket1', dst_path, src_path)
    #             upload_to_s3(target_bucket, dst_path, src_path)
    #
    #         if latest_timestamp is None or timestamp > latest_timestamp:
    #             latest_timestamp = timestamp
    #             latest_file = src_path
    #
    # print('Largest file timestamp:', latest_timestamp)
    # # Store the largest timestamp and persist it to file
    # sync_json[config_key] = latest_timestamp
    # with open('sync.json', 'w', encoding='utf-8') as out_file:
    #     json.dump(sync_json, out_file, indent=4)

