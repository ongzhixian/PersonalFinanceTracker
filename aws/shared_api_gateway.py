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
import re
import json

from datetime import datetime
from typing import Literal
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

import boto3
from botocore.exceptions import ClientError

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
    def __init__(self, account_id:str, api_id:str|None = None, aws_region = 'us-east-1'):
        self.api_gateway_client = boto3.client('apigatewayv2')
        self.lambda_client = boto3.client('lambda')
        self.api_id = api_id
        self.account_id = account_id
        self.aws_region = aws_region

    # CREATE API

    def __create_api(self, name:str, protocol_type:Literal["WEBSOCKET", "HTTP"]):
        response = self.api_gateway_client.create_api(Name=name, ProtocolType=protocol_type)
        print(response)

    def __add_stage(self, stage_name='$default'):
        response = self.api_gateway_client.create_stage(
            ApiId=self.api_id,
            AutoDeploy=True,
            StageName=stage_name
        )
        print(response)

    # def get_stage_list(self):
    #     response = self.api_gateway_client.get_stages(ApiId=self.api_id)
    #     print(response)
    #     #return response['Items']

    def __add_route(self, route_key):
        response = self.api_gateway_client.create_route(
            ApiId=self.api_id,
            RouteKey = route_key
        )
        print(response)

    def create_http_api(self, api_name: str = 'TestHttpApi', route_key_list: list[str] = []):
        """Run a series of steps needed for creating a new HTTP API
        """
        # ONLY FOR CREATING A NEW API
        self.api_gateway_client.__create_api(api_name, 'HTTP')

        ## ADD DEFAULT STAGE (or else it does not get deployed automatically)
        self.api_gateway_client.__add_stage()
        # api_gateway_client.get_stage_list()

        ## ADD ROUTES TO API
        # route_key_list = ['POST /authentication-ticket', 'GET /user-credential', 'GET /membership']
        for route_key in route_key_list:
            self.api_gateway_client.__add_route(route_key)


    # CREATE INTEGRATIONS FOR LAMBDAS

    def __get_integration_list(self):
        response = self.api_gateway_client.get_integrations(ApiId=self.api_id)
        print('INTEGRATIONS')
        print(response)
        response_list = response['Items'] if 'Items' in response else []
        return response_list

    def __get_lambda_list(self, function_partial_name: str = ''):
        lambda_list = []

        list_functions_kwargs = {}
        while True:
            response = self.lambda_client.list_functions(**list_functions_kwargs)
            lambda_list.extend([{
                "FunctionName": func['FunctionName'],
                "Description": func['Description'],
                "FunctionArn": func['FunctionArn'],
                "Runtime": func['Runtime'] if 'Runtime' in func else None
            } for func in response['Functions']])
            if 'NextMarker' in response:
                list_functions_kwargs['Marker'] = response['NextMarker']
            else:
                break

        if len(function_partial_name) <= 0:
            return lambda_list

        return list(filter(lambda lambda_desc: function_partial_name in lambda_desc['FunctionName'], lambda_list))

    def __add_integration(self,
                        integration_uri:str,
                        description:str = '',
                        payload_format_version:str =  '2.0',
                        integration_method: str = 'POST',
                        integration_type:Literal['AWS', 'AWS_PROXY', 'HTTP', 'HTTP_PROXY', 'MOCK'] = 'AWS_PROXY'):
        response = self.api_gateway_client.create_integration(
            ApiId=self.api_id,
            IntegrationMethod = integration_method,
            Description = description,
            PayloadFormatVersion = payload_format_version,
            IntegrationUri = integration_uri,
            IntegrationType = integration_type
        )
        print(response)
        # response_list = response['Items'] if 'Items' in response else []
        # return response_list



    def create_integrations_for_lambdas(self, function_partial_name:str = 'ucm_'):
        """Automation to create integrations for a given set of lambdas
        """
        # CREATE INTEGRATIONS FOR LAMBDAS

        integration_list = self.__get_integration_list()
        integration_uri_list = [integration['IntegrationUri'] for integration in integration_list]
        lambda_list = self.__get_lambda_list(function_partial_name)

        lambda_with_no_integration_list = list(filter(lambda func: func['FunctionArn'] not in integration_uri_list, lambda_list))

        for lambda_func in lambda_with_no_integration_list:
            self.api_gateway_client.__add_integration(lambda_func['FunctionArn'], lambda_func['FunctionName'])

        # print('INTEGRATIONS:')
        # for integration in integration_list:
        #     print(integration)
        # print()
        #
        # integration_uri_list = [integration['IntegrationUri'] for integration in integration_list]
        # lambda_list = get_lambda_list('ucm_')
        # print('LAMBDAS:')
        # for lambda_function in lambda_list:
        #     print(lambda_function)
        # print()
        #
        # lambda_with_no_integration_list = list(filter(lambda func: func['FunctionArn'] not in integration_uri_list, lambda_list))
        # print('Lambdas that are not integrated (count):', len(lambda_with_no_integration_list))
        #
        # for lambda_func in lambda_with_no_integration_list:
        #     print('Adding integration for lambda function:')
        #     print(lambda_func)
        #     api_gateway_client.add_integration(lambda_func['FunctionArn'], lambda_func['FunctionName'])


    # ATTACH INTEGRATIONS TO ROUTES

    def __map_to_lambda(self, integration, lambda_list):
        result = {}
        integration_uri = integration['IntegrationUri']
        lambdas_arn_matching_integration_uri = list(
            filter(lambda func: func['FunctionArn'] == integration_uri, lambda_list))

        if len(lambdas_arn_matching_integration_uri) == 1:
            lambda_func = lambdas_arn_matching_integration_uri[0]
            result = lambdas_arn_matching_integration_uri[0]
            result['IntegrationId'] = integration['IntegrationId']
            result = {
                'IntegrationId': integration['IntegrationId'],
                'FunctionName': lambda_func['FunctionName'],
                'FunctionArn': lambda_func['FunctionArn']
            }
            return result
        else:
            # What if there is more than 1? Or none?
            print('WARNING: Multiple or no mapping for integration id:', integration['IntegrationId'])
            return None
            result = {
                'IntegrationId': integration['IntegrationId']
            }
            return result

    def __get_route_list(self):
        response = self.api_gateway_client.get_routes(ApiId=self.api_id)
        print(response)
        response_list = response['Items'] if 'Items' in response else []
        return response_list
        # return [{
        #     'Name': api['Name'],
        #     'ProtocolType': api['ProtocolType'],
        #     'ApiId': api['ApiId'],
        #     'ApiEndpoint': api['ApiEndpoint']
        # } for api in response_list]

    def __get_integration_id_best_matching(self, route_key, integration_lambda_map):
        # Transform route_key into regex
        # Given 'POST /authentication-ticket'
        # Target regex will be '.*post.*authentication_ticket.*'
        route_parts = route_key.lower().replace('/', '').replace('-', '_').split()
        target_regex = f".*{'.*'.join(route_parts)}.*"


        for integration_lambda in integration_lambda_map:
            re_match = re.match(target_regex, integration_lambda['FunctionName'])
            if re_match is not None:
                return integration_lambda
        return None

    def __attach_integration_to_route(self, route_id, target):
        response = self.api_gateway_client.update_route(
            ApiId=self.api_id,
            RouteId=route_id,
            Target=target
        )
        print(response)

    def add_invoke_function_permission_to_lambda(self, lambda_function_name:str, route_key:str):
        """
        resource_path = '/ucm/membership'
        """
        route_key_parts = route_key.split()
        #http_method = route_key_parts[0] # Hardcode -- default to '*'
        resource_path = route_key_parts[1]
        resource_path = resource_path if resource_path.startswith('/') else f'/{resource_path}'

        # execute-api (HTTP APIs, WebSocket APIs, and REST APIs) ARNs:
        # arn:partition:execute-api:region:account-id:api-id/stage/http-method/resource-path
        # See: https://docs.aws.amazon.com/apigateway/latest/developerguide/arn-format-reference.html#apigateway-execute-api-arns
        source_arn = f"arn:aws:execute-api:{self.aws_region}:{self.account_id}:{self.api_id}/*/*{resource_path}"

        self.lambda_client.add_permission(
            FunctionName=lambda_function_name,
            StatementId='api_gateway_invoke_function',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn
        )

    def attach_integrations_to_routes(self, function_partial_name:str = 'ucm_'):
        integration_list = self.__get_integration_list()
        lambda_list = self.__get_lambda_list(function_partial_name)

        # Map each integration to its function to get function attributes (like name)
        mapped_integration_iter = map(lambda integration: self.__map_to_lambda(integration, lambda_list), integration_list)
        integration_lambda_list = list(filter(lambda func: func is not None, mapped_integration_iter))

        route_list = self.__get_route_list()
        routes_with_no_target_list = list(filter(lambda api_route: 'Target' not in api_route, route_list))

        for route_with_no_target in routes_with_no_target_list:
            suggested_integration = self.__get_integration_id_best_matching(route_with_no_target['RouteKey'], integration_lambda_list)
            if suggested_integration is not None:
                self.__attach_integration_to_route(route_with_no_target['RouteId'], f"integrations/{suggested_integration['IntegrationId']}")
                self.add_invoke_function_permission_to_lambda(suggested_integration['FunctionName'],route_with_no_target['RouteKey'])


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

def main():
    security_token_service_client = boto3.client("sts") # Security Token Service
    account_id = security_token_service_client.get_caller_identity()["Account"]

    api_id = '7pps9elf11'
    #api_id = 'flikx8i3c2'
    api_gateway_client = ApiGatewayClient(account_id=account_id, api_id=api_id)
    # api_gateway_client.create_http_api('UcmHttpApi', ['POST /authentication-ticket', 'GET /user-credential', 'GET /membership'])
    api_gateway_client.create_integrations_for_lambdas()
    api_gateway_client.attach_integrations_to_routes()


def test_api():
    import urllib
    api_base_url = 'https://7pps9elf11.execute-api.us-east-1.amazonaws.com'
    try:
        req = urllib.request.Request(url=f'{api_base_url}/user-credential', method='GET')
        with urllib.request.urlopen(req) as f:
            print(f'HTTP {f.status} ({f.reason})')
            print(f.read().decode('utf-8'))
    except urllib.error.HTTPError as http_error:
        print(http_error)
    # try:
    #     req = urllib.request.Request(url=f'{api_base_url}/authentication-ticket', method='POST')
    #     with urllib.request.urlopen(req) as f:
    #         print(f'HTTP {f.status} ({f.reason})')
    #         print(f.read().decode('utf-8'))
    # except urllib.error.HTTPError as http_error:
    #     print(http_error)

if __name__ == '__main__':
    main()
    #test_api()
