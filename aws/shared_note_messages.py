"""Module for handling messages
Sections:
    Messages
        1. ResertNoteMessage
"""

import json

from shared_messages import Message

# MESSAGES

class ResertNoteMessage(Message):
    """Message for replacing or inserting a generic note record

    1. id
    1. title
    1. content_type
    1. content
    """

    # Field names
    ID_FIELD_NAME = 'id'
    TITLE_FIELD_NAME = 'title'
    CONTENT_TYPE_FIELD_NAME = 'content_type'
    CONTENT_FIELD_NAME = 'content'

    def __init__(self, id:str, title:str, content_type:str, content, user_code:str):
        self.id = id
        self.title = title
        self.content_type = content_type
        self.content = content
        self.user_code = user_code

    def __str__(self):
        return f"id: {self.id}, title: {self.title}"

    def __repr__(self):
        return json.dumps(self.__dict__)

if __name__ == '__main__':
    message = ResertNoteMessage(
        id='generic_1',
        title='Some generic note',
        content_type='plain/text',
        content='hello world',
        user_code = 'SYSTEM_TEST')
