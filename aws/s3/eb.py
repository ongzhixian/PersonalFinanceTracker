"""Audit script to audit and cleanup AWS resources
AWS Resources to Audit:
1. Lambda functions
1. Log groups
1. Eventbridge schedules
"""

import logging
import json
import os
import boto3
from botocore.exceptions import ClientError
import sys

import pdb

logger = logging.getLogger()

boto3.setup_default_session(profile_name='stub-dev')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

lambda_client = boto3.client('lambda')
logs_client = boto3.client('logs')
scheduler_client = boto3.client('scheduler')

def get_lambda_function_list():
    function_list = []
    list_functions_params = {}

    while True:
        print('Loop', list_functions_params)
        response = lambda_client.list_functions(**list_functions_params)
        # print(response)
        if 'Functions' in response:
            # function_list.extend([s3_object['Key'] for s3_object in response['Functions']])
            function_list.extend(response['Functions'])
            print(len(function_list))
        if 'NextMarker' in response:
            list_functions_params['Marker'] = response['NextMarker']
        else:
            break

    print(function_list)
    print(len(function_list))
    with open('function-list.json', 'w') as outfile:
        json.dump(function_list, outfile);

def get_log_groups_list():
    log_groups_list = []
    list_log_groups_params = {}

    ##nextToken='string',)
    while True:
        response = logs_client.list_log_groups(**list_log_groups_params)
        if 'logGroups' in response:
            log_groups_list.extend(response['logGroups'])
        print(response)
        if 'nextToken' in response:
            list_log_groups_params['nextToken'] = response['nextToken']
        else:
            break
    print(log_groups_list)
    print(len(log_groups_list))

def get_schedule_list():
    schedule_list = []
    list_schedules_params = {}

    while True:
        response = scheduler_client.list_schedules(**list_schedules_params)
        print(response)
        if 'Schedules' in response:
            schedule_list.extend(response['Schedules'])
        if 'NextToken' in response:
            list_schedules_params['NextToken'] = response['NextToken']
        else:
            break

    print(schedule_list)
    print(len(schedule_list))


if __name__ == '__main__':
    pass
