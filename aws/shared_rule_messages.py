"""Module for handling messages
Sections:
    Message (object) classes
        Base message classes
            1. Message
            1. OperationResultMessage
            1. ResponseMessage
        other message classes
            1. NewInventoryItemMessage
    Message Service Class(es)
"""

import json

from shared_messages import Message

# CONDITIONs

class Condition(object):
    CONDITION_TYPE_NAME = 'GENERIC'
    def __init__(self, condition_type = None):
        self.condition_type = Condition.CONDITION_TYPE_NAME if condition_type is None else condition_type

    def __str__(self):
        return f"condition_type: {self.condition_type}"

    def __repr__(self):
        return json.dumps(self.__dict__)

    def condition_is_met(self):
        return True

    def to_json(self):
        return json.dumps(self.__dict__)


class AlwaysCondition(Condition):
    CONDITION_TYPE_NAME = 'ALWAYS_CONDITION'
    def __init__(self):
        super().__init__(AlwaysCondition.CONDITION_TYPE_NAME)

    def __str__(self):
        return f"condition_type: {self.condition_type}"

    def __repr__(self):
        return json.dumps(self.__dict__)

    def condition_is_met(self):
        return True

    def to_json(self):
        return json.dumps(self.__dict__)


class SqlCondition(Condition):
    CONDITION_TYPE_NAME = 'SQL_CONDITION'
    HAS_ROWS = 'HAS_ROWS'
    HAS_NO_ROWS = 'HAS_NO_ROWS'

    def __init__(self, data_source:str, sql_statement:str, trigger_condition:str):
        super().__init__(SqlCondition.CONDITION_TYPE_NAME)
        self.data_source = data_source
        self.sql_statement = sql_statement
        self.trigger_condition = trigger_condition

    def __str__(self):
        return f"data_source: {self.data_source}, sql_statement: {self.sql_statement}"

    def __repr__(self):
        return json.dumps(self.__dict__)

    def condition_is_met(self):
        return True

    def to_json(self):
        return json.dumps(self.__dict__)

    def from_json(json:dict):
        condition_type = json['condition_type'] if 'condition_type' in json else None
        data_source = json['data_source'] if 'data_source' in json else None
        sql_statement = json['sql_statement'] if 'sql_statement' in json else None
        trigger_condition = json['trigger_condition'] if 'trigger_condition' in json else None
        return SqlCondition(data_source, sql_statement, trigger_condition)

# OUTPUTS

class Output(object):
    def __init__(self, output_type:str|None):
        self.output_type = 'GENERIC' if output_type is None else output_type

    def to_json(self):
        return json.dumps(self.__dict__)

class OutputHtml(Output):
    def __init__(self, content:str):
        super().__init__('HTML')
        self.content_type = 'text/html'
        self.content = content

    def __str__(self):
        return f"content_type: {self.content_type}, content: {self.content}"

    def __repr__(self):
        return json.dumps(self.__dict__)

    def to_json(self):
        return json.dumps(self.__dict__)

    def from_json(json:dict):
        output_type = json['output_type'] if 'output_type' in json else None
        content_type = json['content_type'] if 'content_type' in json else None
        content = json['content'] if 'content' in json else None
        return OutputHtml(content)

# MESSAGES

class ResertRuleMessage(Message):
    """Message for replacing or inserting a generic record

    1. description
    1. priority         -- 1 - INFO, 2 - WARNING, 3 - ERROR
    1. group            -- netting | marge | core

    1. condition        -- sql_condition | always_condition
    1. trigger(?)       -- on_condition_truthy | on_condition_falsy
    1. condition_type(?)-- sql

    1. effective_from
    1. effective_to
    1. output           -- output

    1. rule_type(?)     -- information

    sql_condition = {
        1. condition_is_met = True if query has rows else False
        1. data_source
        1. query
    }

    always_condition = {
        1. condition_is_met = True
    }

    output = {
        1. content_type
        1. content
    }

    """
    # Field names
    ID_FIELD_NAME = 'id'

    DESCRIPTION_FIELD_NAME = 'description'
    PRIORITY_FIELD_NAME = 'priority'
    GROUP_FIELD_NAME = 'group'

    CONDITION_FIELD_NAME = 'condition'
    #TRIGGER_FIELD_NAME = 'trigger'
    #CONDITION_TYPE_FIELD_NAME = 'condition_type'

    EFFECTIVE_FROM_FIELD_NAME = 'effective_from'
    EFFECTIVE_TO_FIELD_NAME = 'effective_to'
    OUTPUT_FIELD_NAME = 'output'

    RULE_TYPE_FIELD_NAME = 'rule_type'

    def __init__(self, id:str, description:str,  priority:str, group:str, condition: Condition,
                 # trigger:str, condition_type:str,
                 effective_from:str, effective_to:str, output:Output,
                 rule_type:str, user_code:str):
        self.id = id

        self.description = description
        self.priority = priority
        self.group = group
        self.condition = condition
        self.effective_from = effective_from
        self.effective_to = effective_to
        self.output = output

        self.rule_type = rule_type
        self.user_code = user_code

    def __str__(self):
        return f"id: {self.id}, description: {self.description}"

    def __repr__(self):
        return json.dumps(self.__dict__)

class ResertMlpAthenaQualityCheckRuleMessage(Message):
    """Message for replacing or inserting a MLP Athena quality check record
    """
    # Fields in parquet
    # 1. CronSettings
    # 1. DataSource
    # 1. EffectiveFrom
    # 1. EffectiveTo
    # 1. FailureTemplate
    # 1. Query
    # 1. Severity
    # 1. StageName
    # 1. TestId
    # 1. TestName

    # Field names
    CRON_SETTINGS_FIELD_NAME = 'cron_settings'
    DATA_SOURCE_FIELD_NAME = 'data_source'
    EFFECTIVE_FROM_FIELD_NAME = 'effective_from'
    EFFECTIVE_TO_FIELD_NAME = 'effective_to'
    FAILURE_TEMPLATE_FIELD_NAME = 'failure_template'
    QUERY_FIELD_NAME = 'query'

    SEVERITY_FIELD_NAME = 'severity'
    STAGE_NAME_FIELD_NAME = 'stage_name'
    TEST_ID_FIELD_NAME = 'test_id'
    TEST_NAME_FIELD_NAME = 'test_name'

    def __init__(self, cron_settings:str, data_source:str, effective_from:str, effective_to:str, failure_template:str,
                 query:str, severity, stage_name:str, test_id, test_name, user_code):
        self.cron_settings = cron_settings
        self.data_source = data_source
        self.effective_from = effective_from
        self.effective_to = effective_to
        self.failure_template = failure_template
        self.query = query
        self.severity = severity
        self.stage_name = stage_name
        self.test_id = test_id
        self.test_name = test_name
        self.user_code = user_code

    def __str__(self):
        return f"test_id: {self.test_id}, test_name: {self.test_name}"

#
# class BaseConfigurationMessage(Message):
#     ID_FIELD_NAME = 'id'
#     CONTENT_TYPE_FIELD_NAME = 'content_type'
#     CONTENT_FIELD_NAME = 'content'
#
#     RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
#     RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
#     RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
#     RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'
#
#     def __init__(self):
#         self.id = None
#         self.content_type = None
#         self.content = None
#
#         self.record_update_by = None
#         self.record_update_datetime = None
#         self.record_create_by = None
#         self.record_create_datetime = None
#
#     def load_dynamodb_item(self, data:dict):
#         self.id = self.map_from_dynamodb_attribute(data, BaseConfigurationMessage.ID_FIELD_NAME)
#         self.content_type = self.map_from_dynamodb_attribute(data, BaseConfigurationMessage.CONTENT_TYPE_FIELD_NAME)
#         content = self.map_from_dynamodb_attribute(data, BaseConfigurationMessage.CONTENT_FIELD_NAME)
#         match self.content_type:
#             case 'JSON':
#                 self.content = json.loads(content)
#             case 'TEXT':
#                 self.content = content
#             case _:
#                 self.content = content
#
#         self.record_update_by = self.map_from_dynamodb_attribute(data, BaseConfigurationMessage.RECORD_UPDATE_BY_FIELD_NAME)
#         self.record_update_datetime = self.map_from_dynamodb_attribute(data, BaseConfigurationMessage.RECORD_UPDATE_DATETIME_FIELD_NAME)
#         self.record_create_by = self.map_from_dynamodb_attribute(data, BaseConfigurationMessage.RECORD_CREATE_BY_FIELD_NAME)
#         self.record_create_datetime = self.map_from_dynamodb_attribute(data, BaseConfigurationMessage.RECORD_CREATE_DATETIME_FIELD_NAME)
#
#     def __str__(self):
#         """human-readable, informal string representation"""
#         return (f"{BaseConfigurationMessage.ID_FIELD_NAME}: {self.id}, "
#                 f"{BaseConfigurationMessage.CONTENT_TYPE_FIELD_NAME}: {self.content_type},"
#                 f" {BaseConfigurationMessage.CONTENT_FIELD_NAME}: {self.content}, ")
#
#     def __repr__(self):
#         """unambiguous, developer-friendly string representation"""
#         return json.dumps(self.__dict__)
#         # return json.dumps({
#         #     BaseConfigurationMessage.ID_FIELD_NAME : self.id,
#         #     BaseConfigurationMessage.CONTENT_TYPE_FIELD_NAME: self.content_type,
#         #     BaseConfigurationMessage.CONTENT_FIELD_NAME: self.content,
#         #     BaseConfigurationMessage.RECORD_UPDATE_BY_FIELD_NAME: self.record_update_by,
#         #     BaseConfigurationMessage.RECORD_UPDATE_DATETIME_FIELD_NAME: self.record_update_datetime,
#         #     BaseConfigurationMessage.RECORD_CREATE_BY_FIELD_NAME: self.record_create_by,
#         #     BaseConfigurationMessage.RECORD_CREATE_DATETIME_FIELD_NAME: self.record_create_datetime
#         # })


if __name__ == '__main__':
    # def __init__(self, record_id: str, description: str, rule_type: str, rule_priority: str, stage: str, trigger: str,
    #              condition: Condition, condition_type: str, effective_from: str, effective_to: str, output: str,
    #              user_code: str):

    # 1. rule_type(?)     -- information
    # 1. rule_priority    -- 1 - INFO, 2 - WARNING, 3 - ERROR
    # 1. rule_stage       -- netting | marge | core
    #
    # 1. trigger          -- on_condition_truthy | on_condition_falsy
    # 1. condition        -- sql_condition
    # 1. condition_type   -- sql

    message = ResertRuleMessage(
        id='generic_1',
        description='Test generic rule',
        priority = '1',
        group = 'core',
        condition=SqlCondition(data_source='Sql', sql_statement='SELECT NULL AS Result WHERE False', trigger_condition=SqlCondition.HAS_ROWS),
        effective_from = '',
        effective_to = '',
        output = OutputHtml('''
<ul id="results">
{% for result in results %}
    <li>{{  result.result }}</li>
{% endfor %}
</ul>'''),
        user_code = 'SYSTEM_TEST',
        rule_type = 'information')
    print(message)

    condition = SqlCondition(data_source='Sql', sql_statement='SELECT NULL AS Result WHERE False', trigger_condition=SqlCondition.HAS_ROWS)
    print(json.dumps(condition.to_json()))

    condition = Condition()
    print(json.dumps(condition.to_json()))