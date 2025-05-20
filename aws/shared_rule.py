"""
Sections:
    AWS Setup
    Entity classes
        ConfigurationEntity
        ResertConfigurationEntity
    Repository classes
        ConfigurationRepository
"""
import json
from datetime import datetime
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

import boto3
from botocore.exceptions import ClientError

from shared_data_repositories import DynamoDbEntity, BaseRepository
from shared_messages import OperationResultMessage
from shared_rule_messages import ResertRuleMessage, ResertMlpAthenaQualityCheckRuleMessage, SqlCondition, OutputHtml

# AWS SETUP

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
if runtime_dns_domain == 'AD.MLP.COM': reset_tzpath(['C:/Anaconda3/share/zoneinfo'])

boto3.setup_default_session(profile_name=aws_profile)

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

# ENTITY CLASSES

## RULE ENTITY CLASSES

class RuleEntity(DynamoDbEntity):
    """Base Configuration entity class.
    A rule record can have the following fields
    1. id
    1. description
    1. rule_type(?)     -- information
    1. rule_priority    -- 1 - INFO, 2 - WARNING, 3 - ERROR
    1. rule_stage       -- netting | marge | core
    1. trigger          -- on_condition_truthy | on_condition_falsy
    1. condition        -- sql_condition
    1. condition_type   -- sql
    1. effective_from
    1. effective_to
    1. output           -- output

    sql_condition = {
        1. data_source
        1. query
    }

    output = {
        1. content_type
        1. content
    }

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """

    ID_FIELD_NAME = 'id'
    RULE_TYPE_FIELD_NAME = 'rule_type'

    DESCRIPTION_FIELD_NAME = 'description'
    PRIORITY_FIELD_NAME = 'priority'
    GROUP_FIELD_NAME = 'group'

    CONDITION_TYPE_FIELD_NAME = 'condition_type'
    CONDITION_FIELD_NAME = 'condition'

    EFFECTIVE_FROM_FIELD_NAME = 'effective_from'
    EFFECTIVE_TO_FIELD_NAME = 'effective_to'

    OUTPUT_TYPE_FIELD_NAME = 'output_type'
    OUTPUT_FIELD_NAME = 'output'

    RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
    RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
    RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.id = None
        self.rule_type = None

        self.description = None
        self.priority = None
        self.group = None
        self.condition_type = None
        self.condition = None
        self.effective_from = None
        self.effective_to = None
        self.output_type = None
        self.output = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

        if len(args) > 0 and isinstance(args[0], dict):
            self.load_from_dict(args[0])

    def to_dynamodb_item(self):
        """
        record_id='generic_1',

        description='Test generic rule',
        rule_type='information',
        rule_priority='1',
        stage='core',
        trigger='on_condition_truthy',

        condition='SELECT NULL AS Result WHERE False',
        condition_type='sql',
        effective_from='',
        effective_to='',
        output='''
    <ul id="results">
    {% for result in results %}
        <li>{{  result.result }}</li>
    {% endfor %}
    </ul>''',
        user_code='SYSTEM_TEST')
        """
        item = {
            'id': self.dynamodb_null_value() if self.id is None else self.dynamodb_string_value(self.id),
            'rule_type': self.dynamodb_null_value() if self.rule_type is None else self.dynamodb_string_value(self.rule_type),

            'description': self.dynamodb_null_value() if self.description is None else self.dynamodb_string_value(self.description),
            'priority': self.dynamodb_null_value() if self.priority is None else self.dynamodb_string_value(self.priority),
            'group': self.dynamodb_null_value() if self.group is None else self.dynamodb_string_value(self.group),

            'condition_type': self.dynamodb_null_value() if self.condition_type is None else self.dynamodb_string_value(self.condition_type),
            'condition': self.dynamodb_null_value() if self.condition is None else self.dynamodb_string_value(self.condition.to_json()),
            'effective_from': self.dynamodb_null_value() if self.effective_from is None else self.dynamodb_string_value(self.effective_from),
            'effective_to': self.dynamodb_null_value() if self.effective_to is None else self.dynamodb_string_value(self.effective_to),

            'output_type': self.dynamodb_null_value() if self.output_type is None else self.dynamodb_string_value(self.output_type),
            'output': self.dynamodb_null_value() if self.output is None else self.dynamodb_string_value(self.output.to_json()),

            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

    def load_from_dict(self, data:dict):
        self.id = self.map_from_dynamodb_attribute(data, RuleEntity.ID_FIELD_NAME)
        self.rule_type = self.map_from_dynamodb_attribute(data, RuleEntity.RULE_TYPE_FIELD_NAME)

        self.description = self.map_from_dynamodb_attribute(data, RuleEntity.DESCRIPTION_FIELD_NAME)
        self.priority = self.map_from_dynamodb_attribute(data, RuleEntity.PRIORITY_FIELD_NAME)
        self.group = self.map_from_dynamodb_attribute(data, RuleEntity.GROUP_FIELD_NAME)

        self.condition_type = self.map_from_dynamodb_attribute(data, RuleEntity.CONDITION_TYPE_FIELD_NAME)
        condition_json = json.loads(self.map_from_dynamodb_attribute(data, RuleEntity.CONDITION_FIELD_NAME))
        match self.condition_type:
            case 'SQL_CONDITION':
                self.condition = SqlCondition.from_json(condition_json)
            case _:
                self.condition = None

        self.effective_from = self.map_from_dynamodb_attribute(data, RuleEntity.EFFECTIVE_FROM_FIELD_NAME)
        self.effective_to = self.map_from_dynamodb_attribute(data, RuleEntity.EFFECTIVE_TO_FIELD_NAME)

        self.output_type = self.map_from_dynamodb_attribute(data, RuleEntity.OUTPUT_TYPE_FIELD_NAME)
        output_json = json.loads(self.map_from_dynamodb_attribute(data, RuleEntity.OUTPUT_FIELD_NAME))
        match self.output_type:
            case 'HTML':
                self.output = OutputHtml.from_json(output_json)
            case _:
                self.output = None

        self.record_update_by = self.map_from_dynamodb_attribute(data, RuleEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_update_datetime = self.map_from_dynamodb_attribute(data, RuleEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_create_by = self.map_from_dynamodb_attribute(data, RuleEntity.RECORD_CREATE_BY_FIELD_NAME)
        self.record_create_datetime = self.map_from_dynamodb_attribute(data, RuleEntity.RECORD_CREATE_DATETIME_FIELD_NAME)
        pass

        # self.id = self.map_from_dynamodb_attribute(data, ConfigurationEntity.ID_FIELD_NAME)
        # self.content_type = self.map_from_dynamodb_attribute(data, ConfigurationEntity.CONTENT_TYPE_FIELD_NAME)
        # content = self.map_from_dynamodb_attribute(data, ConfigurationEntity.CONTENT_FIELD_NAME)
        # match self.content_type:
        #     case 'JSON':
        #         self.content = json.loads(content)
        #     case 'TEXT':
        #         self.content = content
        #     case _:
        #         self.content = content
        #
        # self.record_update_by = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_UPDATE_BY_FIELD_NAME)
        # self.record_update_datetime = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_UPDATE_DATETIME_FIELD_NAME)
        # self.record_create_by = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_CREATE_BY_FIELD_NAME)
        # self.record_create_datetime = self.map_from_dynamodb_attribute(data, ConfigurationEntity.RECORD_CREATE_DATETIME_FIELD_NAME)


    def __str__(self):
        """human-readable, informal string representation"""
        return (f"{RuleEntity.ID_FIELD_NAME}: {self.id}, "
                f"{RuleEntity.RULE_TYPE_FIELD_NAME}: {self.rule_type}")

    def __repr__(self):
        """unambiguous, developer-friendly string representation"""
        return json.dumps(self.__dict__)

    def to_json_object(self):
        return self.__dict__

    @staticmethod
    def get_record_timestamp() -> datetime:
        # record_timestamp = datetime.now(timezone.utc).as timezone(SINGAPORE_TIMEZONE)
        record_timestamp = datetime.now(SINGAPORE_TIMEZONE)
        return record_timestamp


class ResertRuleEntity(RuleEntity):
    """(Re)place or In(sert) a configuration record."""
    def __init__(self, resert_configuration_message:ResertRuleMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.id = resert_configuration_message.id
        self.rule_type = resert_configuration_message.rule_type

        self.description = resert_configuration_message.description
        self.priority = resert_configuration_message.priority
        self.group = resert_configuration_message.group

        self.condition_type = resert_configuration_message.condition.condition_type
        self.condition = resert_configuration_message.condition

        self.effective_from = resert_configuration_message.effective_from
        self.effective_to = resert_configuration_message.effective_to
        self.output_type = resert_configuration_message.output.output_type
        self.output = resert_configuration_message.output

        self.record_update_by = resert_configuration_message.user_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = resert_configuration_message.user_code
        self.record_create_datetime = record_timestamp


class ResertMlpAthenaQualityCheckRuleEntity(RuleEntity):
    """(Re)place or In(sert) a MLP Athena Quality record."""
    def __init__(self, resert_configuration_message:ResertMlpAthenaQualityCheckRuleMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.cron_settings = resert_configuration_message.cron_settings
        self.data_source = resert_configuration_message.data_source
        self.effective_from = resert_configuration_message.effective_from
        self.effective_to = resert_configuration_message.effective_to
        self.failure_template = resert_configuration_message.failure_template
        self.query = resert_configuration_message.query

        self.severity = resert_configuration_message.severity
        self.stage_name = resert_configuration_message.stage_name
        self.test_id = resert_configuration_message.test_id
        self.test_name = resert_configuration_message.test_name

        self.id = resert_configuration_message.test_id
        self.record_update_by = resert_configuration_message.user_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = resert_configuration_message.user_code
        self.record_create_datetime = record_timestamp

    def to_dynamodb_item(self):
        item = {
            'id': self.dynamodb_null_value() if self.id is None else self.dynamodb_string_value(f"athena-{self.id}"),

            'cron_settings': self.dynamodb_null_value() if self.cron_settings is None else self.dynamodb_string_value(self.cron_settings),
            'data_source': self.dynamodb_null_value() if self.data_source is None else self.dynamodb_string_value(self.data_source),
            'effective_from': self.dynamodb_null_value() if self.effective_from is None else self.dynamodb_string_value(self.effective_from),
            'effective_to': self.dynamodb_null_value() if self.effective_to is None else self.dynamodb_string_value(self.effective_to),
            'failure_template': self.dynamodb_null_value() if self.failure_template is None else self.dynamodb_string_value(self.failure_template),
            'query': self.dynamodb_null_value() if self.query is None else self.dynamodb_string_value(self.query),

            'severity': self.dynamodb_null_value() if self.severity is None else self.dynamodb_string_value(self.severity),
            'stage_name': self.dynamodb_null_value() if self.stage_name is None else self.dynamodb_string_value(self.stage_name),
            'test_id': self.dynamodb_null_value() if self.test_id is None else self.dynamodb_string_value(self.test_id),
            'test_name': self.dynamodb_null_value() if self.id is None else self.dynamodb_string_value(self.test_name),

            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

# REPOSITORY CLASSES

class RuleRepository(BaseRepository):
    """Repository for rule item
    Methods:
        resert_rule
        todo_get_rule
        todo_get_all_rules
    """
    def __init__(self):
        self._TABLE_NAME = 'rule'

    def resert_rule(self, resert_configuration_message:ResertRuleMessage):
        try:
            response = dynamodb_client.put_item(
                TableName = self._TABLE_NAME,
                Item=ResertRuleEntity(resert_configuration_message).to_dynamodb_item(),
                ReturnConsumedCapacity='TOTAL'
            )
            print('put_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')

    def get_rule(self, id:str):
        try:
            response = dynamodb_client.get_item(
                TableName=self._TABLE_NAME,
                Key={ 'id': {'S': id} }
            )
            print('get_item:', response)
            if 'Item' in response:
                # data_obj = self.__data_object_from_dynamodb_response_item(response['Item'])
                # message = BaseConfigurationMessage()
                # message.load_dynamodb_item(response['Item'])
                # entity = ConfigurationEntity(response['Item'])
                # Rebuild
                entity = RuleEntity(response['Item'])
                return OperationResultMessage(
                    True,
                    data_object=RuleEntity(response['Item']).to_json_object())
            return OperationResultMessage(True)

        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')


    # def todo_get_rule(self, record_id:str):
    #     try:
    #         response = dynamodb_client.get_item(
    #             TableName=self.CONFIGURATION_TABLE_NAME,
    #             Key={'id': {'S': record_id}
    #             }
    #         )
    #         print('get_item:', response)
    #         if 'Item' in response:
    #             # data_obj = self.__data_object_from_dynamodb_response_item(response['Item'])
    #             # message = BaseConfigurationMessage()
    #             # message.load_dynamodb_item(response['Item'])
    #             # entity = ConfigurationEntity(response['Item'])
    #             return OperationResultMessage(
    #                 True,
    #                 data_object=ConfigurationEntity(response['Item']).to_json_object())
    #         return OperationResultMessage(True)
    #
    #     except ClientError as client_error:
    #         print('client_error:', client_error)
    #         return OperationResultMessage(False, client_error.response)
    #         # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
    #         #     print('This was not a unique key')
    #         # else:
    #         #     print('some other dynamodb related error')
    #
    # def todo_get_all_rules(self):
    #     try:
    #         response = dynamodb_client.scan(TableName=self.CONFIGURATION_TABLE_NAME)
    #         print('scan:', response)
    #         if 'Items' in response:
    #             result = []
    #             for item in response['Items']:
    #                 # Transform response['Item'] back into JSON-compatible object
    #                 # message = BaseConfigurationMessage()
    #                 # message.load_dynamodb_item(item)
    #                 result.append(ConfigurationEntity(item).to_json_object())
    #             return OperationResultMessage(True, data_object=result)
    #         return OperationResultMessage(True)
    #     except ClientError as client_error:
    #         print('client_error:', client_error)
    #         return OperationResultMessage(False, client_error.response)
    #         # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
    #         #     print('This was not a unique key')
    #         # else:
    #         #     print('some other dynamodb related error'


class ResertMlpAthenaQualityCheckRuleRepository(BaseRepository):
    """Repository for rule item
    Methods:
        resert_rule
        todo_get_rule
        todo_get_all_rules
    """
    def __init__(self):
        self._TABLE_NAME = 'rule'

    def resert_rule(self, resert_configuration_message:ResertMlpAthenaQualityCheckRuleMessage):
        print(ResertMlpAthenaQualityCheckRuleEntity(resert_configuration_message).to_dynamodb_item())
        try:
            response = dynamodb_client.put_item(
                TableName = self._TABLE_NAME,
                Item=ResertMlpAthenaQualityCheckRuleEntity(resert_configuration_message).to_dynamodb_item(),
                ReturnConsumedCapacity='TOTAL'
            )
            print('put_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            print('client_error:', client_error)
            return OperationResultMessage(False, client_error.response)
            # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            #     print('This was not a unique key')
            # else:
            #     print('some other dynamodb related error')

    # def todo_get_rule(self, record_id:str):
    #     try:
    #         response = dynamodb_client.get_item(
    #             TableName=self.CONFIGURATION_TABLE_NAME,
    #             Key={'id': {'S': record_id}
    #             }
    #         )
    #         print('get_item:', response)
    #         if 'Item' in response:
    #             # data_obj = self.__data_object_from_dynamodb_response_item(response['Item'])
    #             # message = BaseConfigurationMessage()
    #             # message.load_dynamodb_item(response['Item'])
    #             # entity = ConfigurationEntity(response['Item'])
    #             return OperationResultMessage(
    #                 True,
    #                 data_object=ConfigurationEntity(response['Item']).to_json_object())
    #         return OperationResultMessage(True)
    #
    #     except ClientError as client_error:
    #         print('client_error:', client_error)
    #         return OperationResultMessage(False, client_error.response)
    #         # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
    #         #     print('This was not a unique key')
    #         # else:
    #         #     print('some other dynamodb related error')
    #
    # def todo_get_all_rules(self):
    #     try:
    #         response = dynamodb_client.scan(TableName=self.CONFIGURATION_TABLE_NAME)
    #         print('scan:', response)
    #         if 'Items' in response:
    #             result = []
    #             for item in response['Items']:
    #                 # Transform response['Item'] back into JSON-compatible object
    #                 # message = BaseConfigurationMessage()
    #                 # message.load_dynamodb_item(item)
    #                 result.append(ConfigurationEntity(item).to_json_object())
    #             return OperationResultMessage(True, data_object=result)
    #         return OperationResultMessage(True)
    #     except ClientError as client_error:
    #         print('client_error:', client_error)
    #         return OperationResultMessage(False, client_error.response)
    #         # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
    #         #     print('This was not a unique key')
    #         # else:
    #         #     print('some other dynamodb related error'


# TESTs

def test_mlp_athena_quality_check_rule_repository():
    rule_repository = ResertMlpAthenaQualityCheckRuleRepository()
    message = ResertMlpAthenaQualityCheckRuleMessage(
        cron_settings='',
        data_source='Sql',
        effective_from='2024-01-01',
        effective_to='2024-12-31',
        failure_template='''
    <ul id="results">
    {% for result in results %}
        <li>{{  result.result }}</li>
    {% endfor %}
    </ul>''',
        query='SELECT NULL AS Result WHERE False',
        severity='1',
        stage_name='core',
        test_id='1',
        test_name='Core Accruals PM Vs Offset Check',
        user_code='SYSTEM_TEST'
    )
    rule_repository.resert_rule(message)

def test_rule_repository():
    message = ResertRuleMessage(
        id='generic_1',                     # Maps to test_id
        description='Test generic rule',    # Maps to test_name
        priority='1',                       # Maps to severity
        group='core',                       # Maps to stage_name
        condition=SqlCondition('Sql', 'SELECT NULL AS Result WHERE False', SqlCondition.HAS_ROWS),
        effective_from='',
        effective_to='',
        output=OutputHtml('''
    <ul id="results">
    {% for result in results %}
        <li>{{  result.result }}</li>
    {% endfor %}
    </ul>'''),
        rule_type='information',
        user_code='SYSTEM_TEST')
    #print(message.__dict__)
    rule_repository = RuleRepository()
    # # rule_repository.resert_rule(message)
    rule = rule_repository.get_rule('generic_1')
    print(rule)

if __name__ == '__main__':
    # Example
    #test_mlp_athena_quality_check_rule_repository()
    test_rule_repository()

    # configuration_repository = ConfigurationRepository()
    # message = ResertConfigurationMessage(
    #     record_id='SYSTEM_TEST_01',
    #     content_type='JSON',
    #     content=json.dumps({
    #         'environment': {
    #             'development': {
    #                 'version': 10
    #             },
    #             'production': {
    #                 'version': 3
    #             }
    #         }
    #     }),
    #     user_code='SYSTEM_TEST')
    #configuration_repository.resert_configuration(message)

    # operation_result_message = configuration_repository.get_configuration('SYSTEM_TEST_01')
    # print(operation_result_message)
    # data_object = operation_result_message.data_object
    # print(operation_result_message.data_object)
    # print(json.dumps(operation_result_message.data_object))
    #
    # operation_result_message = configuration_repository.get_all_configurations()
    # data_object_list = operation_result_message.data_object
    # print(len(data_object_list))
    # print(data_object_list)

