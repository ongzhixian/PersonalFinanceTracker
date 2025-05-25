"""Script to setup routes
Sections:
    1. Setup AWS
    1. Setup AWS Services
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

import re

from typing import Literal

import pdb

logger = logging.getLogger()

# Setup AWS

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
if runtime_dns_domain == 'AD.MLP.COM': reset_tzpath(['C:/Anaconda3/share/zoneinfo'])

boto3.setup_default_session(profile_name=aws_profile)

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

# AWS services

# s3 = boto3.resource('s3')
# s3_client = boto3.client('s3')
# lambda_client = boto3.client('lambda')
# logs_client = boto3.client('logs')
# scheduler_client = boto3.client('scheduler')
#api_gateway_client = boto3.client('apigatewayv2')





class ApiGatewayClient(object):
    def __init__(self, api_id:str|None = None):
        self.api_gateway_client = boto3.client('apigatewayv2')
        self.api_id = api_id

    def create_api(self, name:str, protocol_type:Literal["WEBSOCKET", "HTTP"]):
        response = self.api_gateway_client.create_api(Name=name, ProtocolType=protocol_type)
        print(response)

    def get_integration_list(self):
        response = self.api_gateway_client.get_integrations(ApiId=self.api_id)
        response_list = response['Items'] if 'Items' in response else []
        return response_list

    def add_integration(self,
                        integration_uri:str,
                        description:str = '',
                        integration_method: str = 'POST',
                        integration_type:Literal['AWS', 'AWS_PROXY', 'HTTP', 'HTTP_PROXY', 'MOCK'] = 'AWS_PROXY'):
        # # {'ConnectionType': 'INTERNET', 'IntegrationId': 'q6lu8lm',
        # 'IntegrationMethod': 'POST',
        # 'IntegrationType': 'AWS_PROXY',
        # 'IntegrationUri': 'arn:aws:lambda:us-east-1:009167579319:function:get-appUser',
        # 'PayloadFormatVersion': '2.0', 'TimeoutInMillis': 30000}
        response = self.api_gateway_client.create_integration(
            ApiId=self.api_id,
            IntegrationMethod = integration_method,
            Description = description,
            IntegrationUri = integration_uri,
            IntegrationType = integration_type
        )
        print(response)
        # response_list = response['Items'] if 'Items' in response else []
        # return response_list

    def get_route_list(self):
        response = self.api_gateway_client.get_routes(ApiId=self.api_id)
        response_list = response['Items'] if 'Items' in response else []
        return response_list
        # return [{
        #     'Name': api['Name'],
        #     'ProtocolType': api['ProtocolType'],
        #     'ApiId': api['ApiId'],
        #     'ApiEndpoint': api['ApiEndpoint']
        # } for api in response_list]

    def add_route(self, route_key):
        response = self.api_gateway_client.create_route(
            ApiId=self.api_id,
            RouteKey = route_key
        )
        print(response)

    def get_api_list(self):
        response = self.api_gateway_client.get_apis()
        response_list = response['Items'] if 'Items' in response else []
        return [{
            'Name': api['Name'],
            'ProtocolType': api['ProtocolType'],
            'ApiId': api['ApiId'],
            'ApiEndpoint': api['ApiEndpoint']
        } for api in response_list ]
        #
        # for api in response_list:
        #     print(
        #         f"\nProtocolType: {api['ProtocolType']:<10}, ApiId: {api['ApiId']::<10}, ApiEndpoint: {api['ApiEndpoint']}")
        #     print(f"{'':>4}{api}")
        #     item_list.append({
        #         'Name': api['Name'],
        #         'ProtocolType': api['ProtocolType'],
        #         'ApiId': api['ApiId'],
        #         'ApiEndpoint': api['ApiEndpoint']
        #     })

# Examples

def __print_api_list(api_list):
    print(f"Number of APIs: {len(api_list)}")
    for api in api_list:
        print(f"Name: {api['Name']:<12}, "
              f"ProtocolType: {api['ProtocolType']:<10}, "
              f"ApiId: {api['ApiId']:<10}, "
              f"ApiEndpoint: {api['ApiEndpoint']}")

def get_lambda_list(function_name:str = ''):
    lambda_list = []
    lambda_client = boto3.client('lambda')

    list_functions_kwargs = {}
    while True:
        response = lambda_client.list_functions(**list_functions_kwargs)
        # for func in response['Functions']:
        #     if 'Runtime' not in func:
        #         print(func)
        lambda_list.extend([{
            "FunctionName": func['FunctionName'],
            "Description": func['Description'],
            "FunctionArn": func['FunctionArn'],
            "Runtime": func['Runtime'] if 'Runtime' in func else None
        } for func  in response['Functions']])
        if 'NextMarker' in response:
            list_functions_kwargs['Marker'] = response['NextMarker']
        else:
            break

    print(f'Total number of lambdas scanned: {len(lambda_list)}')
    if len(function_name) > 0:
        filtered_list = list(filter(lambda lambda_desc: function_name in lambda_desc['FunctionName'], lambda_list))
    else:
        filtered_list = lambda_list
    print(f'Total filtered lambdas: {len(filtered_list)}')
    return filtered_list

def main():
    api_id = '7pps9elf11'
    #api_id = 'flikx8i3c2'
    api_gateway_client = ApiGatewayClient(api_id)
    #api_gateway_client.create_api('UcmHttpApi', 'HTTP')

    # route_key_list = ['POST /authentication-ticket', 'GET /user-credential', 'GET /membership']
    # for route_key in route_key_list:
    #     api_gateway_client.add_route(route_key)

    lambda_list = get_lambda_list('ucm_')

    #api_gateway_client.add_integration()


    # integration_list = api_gateway_client.get_integration_list()
    # print(integration_list)

    # {'ConnectionType': 'INTERNET', 'IntegrationId': 'oqd67cn', 'IntegrationMethod': 'POST', 'IntegrationType': 'AWS_PROXY', 'IntegrationUri': 'arn:aws:lambda:us-east-1:009167579319:function:basic-lambda', 'PayloadFormatVersion': '2.0', 'TimeoutInMillis': 30000},
    # {'ConnectionType': 'INTERNET', 'IntegrationId': 'q6lu8lm', 'IntegrationMethod': 'POST', 'IntegrationType': 'AWS_PROXY', 'IntegrationUri': 'arn:aws:lambda:us-east-1:009167579319:function:get-appUser', 'PayloadFormatVersion': '2.0', 'TimeoutInMillis': 30000}

    # route_list = api_gateway_client.get_route_list()
    # print(route_list)

    # api_list = api_gateway_client.get_api_list()
    # __print_api_list(api_list)


if __name__ == '__main__':
    main()
