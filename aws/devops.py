"""DevOps script
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

boto3.setup_default_session(profile_name=aws_profile)

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

# AWS services

iam_client = boto3.client('iam')

# s3 = boto3.resource('s3')
# s3_client = boto3.client('s3')

# lambda_client = boto3.client('lambda')
# logs_client = boto3.client('logs')
# scheduler_client = boto3.client('scheduler')

# def get_lambda_function_list():
#     function_list = []
#     list_functions_params = {}

#     while True:
#         print('Loop', list_functions_params)
#         response = lambda_client.list_functions(**list_functions_params)
#         # print(response)
#         if 'Functions' in response:
#             # function_list.extend([s3_object['Key'] for s3_object in response['Functions']])
#             function_list.extend(response['Functions'])
#             print(len(function_list))
#         if 'NextMarker' in response:
#             list_functions_params['Marker'] = response['NextMarker']
#         else:
#             break

#     print(function_list)
#     print(len(function_list))
#     with open('function-list.json', 'w') as outfile:
#         json.dump(function_list, outfile);

# def get_log_groups_list():
#     log_groups_list = []
#     list_log_groups_params = {}

#     ##nextToken='string',)
#     while True:
#         response = logs_client.list_log_groups(**list_log_groups_params)
#         if 'logGroups' in response:
#             log_groups_list.extend(response['logGroups'])
#         print(response)
#         if 'nextToken' in response:
#             list_log_groups_params['nextToken'] = response['nextToken']
#         else:
#             break
#     print(log_groups_list)
#     print(len(log_groups_list))

# def get_schedule_list():
#     schedule_list = []
#     list_schedules_params = {}

#     while True:
#         response = scheduler_client.list_schedules(**list_schedules_params)
#         print(response)
#         if 'Schedules' in response:
#             schedule_list.extend(response['Schedules'])
#         if 'NextToken' in response:
#             list_schedules_params['NextToken'] = response['NextToken']
#         else:
#             break

#     print(schedule_list)
#     print(len(schedule_list))
#     return schedule_list

def get_role_list():
    list_roles_response = iam_client.list_roles()
    roles = list_roles_response.get('Roles', [])
    return [role['RoleName'] for role in roles]

def get_user_list():
    list_users_response = iam_client.list_users()
    user_list = list_users_response.get('Users', [])
    return [user['UserName'] for user in user_list]

class Group():
    def __init__(self, iam_client):
        self.client = iam_client

    def get_group_list(self):
        list_groups_response = self.client.list_groups()
        group_list = list_groups_response.get('Groups', [])
        return [group['GroupName'] for group in group_list]
    
    def create_group(self, group_name):
        response = self.client.create_group(GroupName=group_name)
        print(response)

    def delete_group(self, group_name):
        response = self.client.delete_group(GroupName=group_name)
        print(response)

    def group_exists(self, group_name):
        try:
            self.client.get_group(GroupName=group_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                return False
            else:
                raise e
        
class Policy():
    def __init__(self, iam_client):
        self.client = iam_client

    def get_policy_list(self):
        # Scope='All'|'AWS'|'Local'
        list_policies_response = self.client.list_policies(Scope='Local')
        policy_list = list_policies_response.get('Policies', [])
        return [policy['PolicyName'] for policy in policy_list]

    def create_policy(self, policy_name, policy_document):
        response = self.client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(response)

    def delete_policy(self, policy_arn):
        response = self.client.delete_policy(PolicyArn=policy_arn)
        print(response)

    def policy_exists(self, policy_name):
        policy_list = self.get_policy_list()
        return policy_name in policy_list

    def get_policy_by_arn(self, arn:str):
        response = self.client.get_policy(PolicyArn=arn)
        print(response)

    def get_policy_by_name(self, policy_name):
        list_policies_response = self.client.list_policies(Scope='Local')
        policy_list = list_policies_response.get('Policies', [])
        for policy in policy_list:
            if policy['PolicyName'] == policy_name:
                return policy
        return None

    def delete_policy_by_name(self, policy_name):
        policy = self.get_policy_by_name(policy_name)
        if policy:
            self.delete_policy(policy['Arn'])
        else:
            print(f"Policy '{policy_name}' not found.")

class Role():
    def __init__(self, iam_client):
        self.client = iam_client

    def get_role_list(self):
        list_roles_response = self.client.list_roles()
        role_list = list_roles_response.get('Roles', [])
        print_list(role_list, "IAM Roles")
        return [role['RoleName'] for role in role_list]
    
    def get_role(self, role_name):
        response = self.client.get_role(RoleName=role_name)
        return response

    def create_role(self, role_name, assume_role_policy_document):
        response = self.client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
        )
        return response

    def delete_role(self, role_name):
        response = self.client.delete_role(RoleName=role_name)
        return response


class User():
    def __init__(self, iam_client):
        self.client = iam_client

    def get_user_list(self):
        list_users_response = self.client.list_users()
        user_list = list_users_response.get('Users', [])
        return [user['UserName'] for user in user_list]

    def create_user(self, user_name):
        response = self.client.create_user(UserName=user_name)
        return response

    def delete_user(self, user_name):
        response = self.client.delete_user(UserName=user_name)
        return response

    def user_exists(self, user_name):
        try:
            self.client.get_user(UserName=user_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                return False
            else:
                raise e

# Utility functions
def print_list(item_list, title="Items"):
    print(f"\n{title}:")
    for item in item_list:
        print(f"{item}")


def main():
    
    user_list = get_user_list()
    print_list(user_list, "Users")
    pass


def test_group():
    group = Group(iam_client)
    group_list = group.get_group_list()
    print_list(group_list, "Groups")
    # group.create_group("test-group")
    group.delete_group("test-group")

def test_policy():
    policy = Policy(iam_client)
    policy_list = policy.get_policy_list()
    print_list(policy_list, "Policies")
    # p = policy.get_policy_by_name('test-policy')
    # print(p)
    # print('Policy ARN: ', p['Arn'] if p else 'Policy not found')
    policy.create_policy(
        policy_name='test-policy',
        policy_document={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreateGroup",
                        "iam:DeleteGroup",
                        "iam:AddUserToGroup",
                        "iam:RemoveUserFromGroup",
                        "iam:ListGroups",
                        "iam:ListGroupsForUser",
                        "iam:ListGroupPolicies",
                        "iam:GetGroup",
                        "iam:GetGroupPolicy",
                        "iam:UpdateGroup"
                    ],
                    "Resource": "*"
                }
            ]
        }
    )
    # policy.delete_policy('arn:aws:iam::123456789012:policy/test-policy')
    # policy.delete_policy_by_name('test-policy')

def test_role():
    role_mgr = Role(iam_client)
    role_list = role_mgr.get_role_list()
    print_list(role_list, "Roles")
    # role = role_mgr.get_role('lambda-developer')
    # print(f"Role Name: {role}")
    # response = role_mgr.create_role(
    #     role_name='test-role', 
    #     assume_role_policy_document=
    #     {
    #         "Version": "2012-10-17",
    #         "Statement": [
    #             {
    #                 'Sid': '', 
    #                 'Effect': 'Allow', 
    #                 'Principal': {
    #                     'Service': 'lambda.amazonaws.com'
    #                 }, 
    #                 'Action': 'sts:AssumeRole'
    #             }
    #         ]
    #     })
    # print(f"Role Created: {response}")
    response = role_mgr.delete_role(role_name='test-role')
    print(f"Role Deleted: {response}")

def test_user():
    pass
    

if __name__ == '__main__':
    # main()
    #test_group()
    # test_policy()
    # test_role()
    test_user()
