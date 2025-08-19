"""
Sections:
    AWS Setup
    Entity classes
        NoteEntity
        ResertNoteEntity
    Repository classes
        NoteRepository
"""
import json
from datetime import datetime
from os import environ
from zoneinfo import ZoneInfo, reset_tzpath

import boto3
from botocore.exceptions import ClientError

from shared_data_repositories import DynamoDbEntity, BaseRepository
from shared_messages import OperationResultMessage
from shared_note_messages import ResertNoteMessage

import pdb

# AWS SETUP

runtime_dns_domain = environ.get('USERDNSDOMAIN')
aws_profile = 'stub-dev' if runtime_dns_domain == 'AD.MLP.COM' else None
if runtime_dns_domain == 'AD.MLP.COM': reset_tzpath(['C:/Anaconda3/share/zoneinfo'])

boto3.setup_default_session(profile_name=aws_profile)

dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

SINGAPORE_TIMEZONE = ZoneInfo("Asia/Singapore")

# ENTITY CLASSES

## COUNTER ENTITY CLASSES

class NoteEntity(DynamoDbEntity):
    """Base Note entity class.
    A note record can have the following fields
    1. id
    1. title
    1. content_type
    1. content

    1. record_update_by
    1. record_update_datetime
    1. record_create_by
    1. record_create_datetime
    """

    ID_FIELD_NAME = 'id'
    TITLE_FIELD_NAME = 'title'
    CONTENT_TYPE_FIELD_NAME = 'content_type'
    CONTENT_FIELD_NAME = 'content'

    RECORD_UPDATE_BY_FIELD_NAME = 'record_update_by'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'record_update_datetime'
    RECORD_CREATE_BY_FIELD_NAME = 'record_create_by'
    RECORD_CREATE_DATETIME_FIELD_NAME = 'record_create_datetime'

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.id = None
        self.title = None
        self.content_type = None
        self.content = None

        self.record_update_by = None
        self.record_update_datetime = None
        self.record_create_by = None
        self.record_create_datetime = None

        if len(args) > 0 and isinstance(args[0], dict):
            self.load_from_dict(args[0])

    def to_dynamodb_item(self):
        """
        """
        item = {
            'id': self.dynamodb_null_value() if self.id is None else self.dynamodb_string_value(self.id),
            'title': self.dynamodb_null_value() if self.title is None else self.dynamodb_string_value(self.title),
            'content_type': self.dynamodb_null_value() if self.content_type is None else self.dynamodb_string_value(self.content_type),
            'content': self.dynamodb_null_value() if self.content is None else self.dynamodb_string_value(self.content),

            'record_update_by': self.dynamodb_null_value() if self.record_update_by is None else self.dynamodb_string_value(self.record_update_by),
            'record_update_datetime': self.dynamodb_null_value() if self.record_update_datetime is None else self.dynamodb_string_value(self.record_update_datetime.isoformat()),
            'record_create_by': self.dynamodb_null_value() if self.record_create_by is None else self.dynamodb_string_value(self.record_create_by),
            'record_create_datetime': self.dynamodb_null_value() if self.record_create_datetime is None else self.dynamodb_string_value(self.record_create_datetime.isoformat())
        }
        return item

    def load_from_dict(self, data:dict):
        self.id = self.map_from_dynamodb_attribute(data, NoteEntity.ID_FIELD_NAME)
        self.title = self.map_from_dynamodb_attribute(data, NoteEntity.TITLE_FIELD_NAME)
        self.content_type = self.map_from_dynamodb_attribute(data, NoteEntity.CONTENT_TYPE_FIELD_NAME)
        self.content = self.map_from_dynamodb_attribute(data, NoteEntity.CONTENT_FIELD_NAME)

        self.record_update_by = self.map_from_dynamodb_attribute(data, NoteEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_update_datetime = self.map_from_dynamodb_attribute(data, NoteEntity.RECORD_UPDATE_BY_FIELD_NAME)
        self.record_create_by = self.map_from_dynamodb_attribute(data, NoteEntity.RECORD_CREATE_BY_FIELD_NAME)
        self.record_create_datetime = self.map_from_dynamodb_attribute(data, NoteEntity.RECORD_CREATE_DATETIME_FIELD_NAME)

    def __str__(self):
        """human-readable, informal string representation"""
        return (f"{NoteEntity.ID_FIELD_NAME}: {self.id}, "
                f"{NoteEntity.TITLE_FIELD_NAME}: {self.title}")

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


class ResertNoteEntity(NoteEntity):
    """(Re)place or In(sert) a note record."""
    def __init__(self, resert_note_message:ResertNoteMessage):
        super().__init__()
        record_timestamp = self.get_record_timestamp()

        self.id = resert_note_message.id
        self.title = resert_note_message.title
        self.content_type = resert_note_message.content_type
        self.content = resert_note_message.content

        self.record_update_by = resert_note_message.user_code
        self.record_update_datetime = record_timestamp
        self.record_create_by = resert_note_message.user_code
        self.record_create_datetime = record_timestamp


# REPOSITORY CLASSES

class NoteRepository(BaseRepository):
    """Repository for note item
    Methods:
        resert_note
    """
    def __init__(self):
        self._TABLE_NAME = 'note'

    def resert_note(self, resert_note_message:ResertNoteMessage):
        put_item_kwargs = {
            'TableName' : self._TABLE_NAME,
            'Item': ResertNoteEntity(resert_note_message).to_dynamodb_item(),
            'ReturnConsumedCapacity': 'TOTAL',
            #'ConditionExpression': 'attribute_not_exists(id)'
        }
        try:
            response = dynamodb_client.put_item(**put_item_kwargs)
            #print('put_item:', response)
            return OperationResultMessage(True)
        except ClientError as client_error:
            error = client_error.response['Error'] if 'Error' in client_error.response else None
            if error is None: return OperationResultMessage(False, client_error.response)
            error_code = error['Code'] if 'Code' in error else None
            print('error', error)
            match error_code:
                case 'ConditionalCheckFailedException':
                    return OperationResultMessage(
                        False,
                        f"Error code: {error_code}, ConditionExpression: {put_item_kwargs['ConditionExpression']}",
                        data_object=resert_note_message)
                case 'ValidationException':
                    return OperationResultMessage(
                        False,
                        f"Error code: {error_code}, Error message: {error['Message']}",
                        data_object=resert_note_message)
                case _:
                    return OperationResultMessage(False, error)

    def get_all_notes(self, id:str):
        print(id)
        response = dynamodb_client.scan(
            TableName=self._TABLE_NAME,
            FilterExpression='#id = :id',
            ExpressionAttributeNames={
                '#id': 'id'
            },
            ExpressionAttributeValues={
                ':id': {'S': id}
            })
        note_list = []
        if 'Items' in response:
            item_list = response['Items']
            for item_dict in item_list:
                note_list.append(NoteEntity(item_dict))

        print(response)
        return note_list


# TESTs

def test_repository():
    note_repository = NoteRepository()
    message = ResertNoteMessage(
        id='generic_1',
        title='Some generic note',
        content_type='plain/text',
        content='hello workd',
        user_code = 'SYSTEM_TEST')
    operation_result_message = note_repository.resert_note(message)
    print('operation_result_message', operation_result_message)

def send_diff_to_notes():
    import os
    import subprocess
    repo_root_path = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('utf8').strip()
    norm_repo_root_path = os.path.normpath(repo_root_path)

    note_repository = NoteRepository()
    file_path_list = []
    with open('diff-to-notes-filelist.txt', 'r', encoding='utf8') as in_file:
        file_path_list = [ line.strip() for line in in_file.readlines() ]
    print(file_path_list)
    for file_path in file_path_list:
        norm_file_path = os.path.normpath(file_path)
        print('Reading', norm_file_path)
        with open(norm_file_path, 'r', encoding='utf8') as in_file:
            content = in_file.read()
        title = norm_file_path.replace(norm_repo_root_path, '')
        message = ResertNoteMessage(
            id=title,
            title=title,
            content_type='plain/text',
            content=content,
            user_code='SYSTEM_TEST')
        operation_result_message = note_repository.resert_note(message)
        print('operation_result_message', operation_result_message)

def get_diff_notes():
    note_repository = NoteRepository()
    all_note_list = note_repository.get_all_notes(f'\\aws\\s3\\exa.txt')
    print(all_note_list)

if __name__ == '__main__':
    # Example
    #test_repository()
    send_diff_to_notes()
    #get_diff_notes()
