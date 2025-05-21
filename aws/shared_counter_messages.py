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

# MESSAGES

class ResertCounterMessage(Message):
    """Message for replacing or inserting a generic record

    1. id
    1. value
    1. description
    """

    # Field names
    ID_FIELD_NAME = 'id'
    VALUE_FIELD_NAME = 'value'
    DESCRIPTION_FIELD_NAME = 'description'

    def __init__(self, id:str, description:str, user_code:str, value:str = '0'):
        self.id = id
        self.value = value
        self.description = description
        self.user_code = user_code

    def __str__(self):
        return f"id: {self.id}, description: {self.description}"

    def __repr__(self):
        return json.dumps(self.__dict__)

class IncrementCounterMessage(Message):
    ID_FIELD_NAME = 'id'

    def __init__(self, id: str, user_code: str):
        self.id = id
        self.user_code = user_code

    def __str__(self):
        return f"id: {self.id}"

    def __repr__(self):
        return json.dumps(self.__dict__)


if __name__ == '__main__':
    message = ResertCounterMessage(
        id='generic_1',
        description='Some generic counter',
        user_code = 'SYSTEM_TEST')
