import boto3
import json
import time
from botocore.exceptions import ClientError

from example_common_aws import setup_aws_profile

setup_aws_profile()
scheduler_client = boto3.client('scheduler')

class EventBridgeScheduler:
    def __init__(self):
        self.scheduler_client = boto3.client('scheduler')
    
    def get_schedule_groups(self):
        try:
            response = self.scheduler_client.list_schedule_groups()
            return [
                {
                    'Name': group.get('Name', ''),
                    'Arn': group.get('Arn', ''),
                    'State': group.get('State', '')
                }
                for group in response.get('ScheduleGroups', [])
            ]
        except ClientError as e:
            print(f"Error listing schedule groups: {e}")
            return []

    def get_schedules(self):
        try:
            response = self.scheduler_client.list_schedules()
            return [
                {
                    'Name': schedule.get('Name', ''),
                    'GroupName': schedule.get('GroupName', ''),
                    'Arn': schedule.get('Arn', ''),
                    'State': schedule.get('State', '')
                }
                for schedule in response.get('Schedules', [])
            ]
        except ClientError as e:
            print(f"Error listing schedules: {e}")
            return []

    def get_schedule(self, name):
        try:
            response = self.scheduler_client.get_schedule(Name=name)
            print(response)
            return {
                'Name': response.get('Name', ''),
                'Arn': response.get('Arn', ''),
                'State': response.get('State', ''),
                'ScheduleExpression': response.get('ScheduleExpression', ''),
                'Target': response.get('Target', {}),
                'FlexibleTimeWindow': response.get('FlexibleTimeWindow', {})
            }
        except ClientError as e:
            print(f"Error getting schedule: {e}")
            return None
        
    def create_schedule(self, name, schedule_expression, target_arn, role_arn, input_data=None):
        try:
            response = self.scheduler_client.create_schedule(
                Name=name,
                ScheduleExpression=schedule_expression,
                Target={
                    'Arn': 'arn:aws:sns:us-east-1:009167579319:example-topic',
                    'RoleArn': role_arn,
                    'Input': json.dumps(input_data) if input_data else None
                },
                FlexibleTimeWindow={
                    'Mode': 'OFF'
                },
                State='ENABLED'
            )
            return response
        except ClientError as e:
            print(f"An error occurred: {e}")
            return None




def main():
    scheduler = EventBridgeScheduler()
    # response = scheduler.get_schedules()
    # print(response)

    response = scheduler.get_schedule("test-eventbridge-schedule")
    print(response)

    # response = scheduler_client.list_schedules()
    # print(response)
    # response = scheduler_client.list_schedule_groups()
    # schedule_groups = response.get('ScheduleGroups', [])
    # for group in schedule_groups:
    #     print(f"Schedule Group: {group['Name']}, Arn: {group['Arn']}, State: {group['State']}")

    
    # scheduler = EventBridgeScheduler(
    #     name='MyDailySchedule',
    #     schedule_expression='cron(0 9 * * ? *)',
    #     target_arn='arn:aws:lambda:us-east-1:123456789012:function:MyLambdaFunction',
    #     role_arn='arn:aws:iam::123456789012:role/EventBridgeSchedulerRole',
    #     input_data={"key": "value"}
    # )
    # response = scheduler.create_schedule()
    # print(response)
    #     ScheduleExpression='cron(0 9 * * ? *)',  # Example: 9 AM UTC daily
    #     Target={
    #         'Arn': 'arn:aws:lambda:us-east-1:123456789012:function:MyLambdaFunction',
    #         'RoleArn': 'arn:aws:iam::123456789012:role/EventBridgeSchedulerRole',
    #         'Input': '{"key": "value"}'  # Optional input for the target
    #     },
    #     FlexibleTimeWindow={
    #         'Mode': 'OFF'
    #     },
    #     State='ENABLED'
    # )
    # print(response)


if __name__ == '__main__':
    main()