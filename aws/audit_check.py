"""Audit script to audit and cleanup AWS resources
AWS Resources to Audit:
1. Lambda functions
1. Log groups
1. Eventbridge schedules
"""

import logging
import json
import boto3
from datetime import datetime
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath
from botocore.exceptions import ClientError



import pdb

logger = logging.getLogger()

# AWS SETUP

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
if runtime_dns_domain == 'AD.MLP.COM': reset_tzpath(['C:/Anaconda3/share/zoneinfo'])
print('runtime_dns_domain', runtime_dns_domain)

boto3.setup_default_session(profile_name=aws_profile)

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

# AWS services

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
    return schedule_list


if __name__ == '__main__':
    # schedule_list = get_schedule_list()
    # print('schedule_list', schedule_list)
    response = scheduler_client.get_schedule(GroupName='default', Name='test-eventbridge-schedule')
    upd = response.copy()
    del upd['ResponseMetadata']
    del upd['CreationDate']
    del upd['LastModificationDate']
    del upd['Arn']
    #print('response', response)

    ts = datetime.now(SINGAPORE_TIMEZONE)
    upd['ScheduleExpression'] = f"cron(*/5 {ts.hour} {ts.day} {ts.month} ? {ts.year})"
    print('upd', upd)

    response = scheduler_client.update_schedule(**upd)
    print('response', response)

    # upd = {}
    # upd['Name'] = response['Name']
    # upd['Description'] = response['Description']
    # upd['ResponseMetadata'] = response['ResponseMetadata']
    # upd['Arn'] = response['Arn']
    # upd['GroupName'] = response['GroupName']
    #
    # upd['FlexibleTimeWindow'] = response['FlexibleTimeWindow']
    # upd['ScheduleExpression'] = response['ScheduleExpression']                  # "cron(*/5 16 21 5 ? 2025)"
    # upd['ScheduleExpressionTimezone'] = response['ScheduleExpressionTimezone']  # "Asia/Singapore"
    # upd['Target'] = response['Target']
    # # "ScheduleExpression": "cron(*/5 16 21 5 ? 2025)",
    # # "ScheduleExpressionTimezone": "Asia/Singapore",
    # print('upd', upd)
    #
