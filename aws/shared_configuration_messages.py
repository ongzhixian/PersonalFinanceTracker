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

from shared_messages import Message

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


class ResertConfigurationMessage(Message):
    """Message for replacing or inserting a configuration record
    """
    # Field names
    ID_FIELD_NAME = 'id'
    CONTENT_TYPE_FIELD_NAME = 'content_type'
    CONTENT_FIELD_NAME = 'content'
    USER_CODE_FIELD_NAME = 'userCode'

    def __init__(self, record_id:str, content_type:str, content:str, user_code:str):
        self.id = record_id
        self.content_type = content_type
        self.content = content
        self.user_code = user_code

    def __str__(self):
        return f"id: {self.id}, content_type: {self.content_type}, content: {self.content}"
