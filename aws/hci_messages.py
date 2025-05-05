"""Module for handling messages
Sections:
    Message (object) classes
        Base message classes
        other message classes
    Message Service Class(es)
"""

import json

# MESSAGE CLASSES

## BASE MESSAGE CLASSES

class Message(object):
    """Base class for all messages"""
    pass

class OperationResultMessage(Message):
    def __init__(self, operation_is_successful: bool, message: str | None = None, data_object: dict | None = None):
        self.is_success = operation_is_successful
        self.message = message
        self.data_object = data_object

    def __str__(self):
        return f"Operation is successful:{self.is_success}, Message:{self.message}, DataObject:{self.data_object}"

class ResponseMessage(Message):
    def __init__(self, status_code:int, body:str):
        self.statusCode = status_code
        self.body = body

    def to_dict(self):
        return {
            'statusCode': self.statusCode,
            'body': self.body
        }

    def __repr__(self):
        return self.to_dict()

    def __str__(self):
        return f"statusCode: {self.statusCode}, body: {self.body}"


## OTHER MESSAGE CLASSES

class NewInventoryItemMessage(Message):
    """Message for creating a new inventory item
    """
    # Field names
    ITEM_CODE_FIELD_NAME = 'itemCode'
    ACTOR_CODE_FIELD_NAME = 'actorCode'

    def __init__(self, item_code:str, actor_code:str):
        self.item_code = item_code
        self.actor_code = actor_code

    def __str__(self):
        return f"Item code:{self.item_code}"

class BorrowInventoryItemMessage(Message):
    """Message for a borrowing a new inventory item
        """
    # Field names
    UPDATE_TYPE_FIELD_NAME = 'updateType'
    BORROWER_CODE_FIELD_NAME = 'borrowerCode'
    ITEM_CODE_FIELD_NAME = 'itemCode'
    USER_CODE_FIELD_NAME = 'userCode'

    def __init__(self, type:str, borrower_code:str, item_code: str, user_code: str):
        self.type = type
        self.borrower_code = borrower_code
        self.item_code = item_code
        self.user_code = user_code

    def __str__(self):
        return f"Type: {self.type}, Borrower Code: {self.borrower_code}, Item code:{self.item_code}, User code: {self.user_code}"

# MESSAGE SERVICE CLASSES

class HciMessageService(object):
    """A service object for creating messages"""

    def create_new_inventory_item_message(self, json:dict) -> NewInventoryItemMessage|None:
        """Create NewInventoryItemMessage if json contains valid data
        Args:
            json (dict): data to create NewInventoryItemMessage
        Returns:
            NewInventoryItemMessage: if json args contain valid information to create NewInventoryItemMessage
            None: if json args does not contain valid information to create NewInventoryItemMessage
        """
        if NewInventoryItemMessage.ITEM_CODE_FIELD_NAME not in json: return None
        if NewInventoryItemMessage.ACTOR_CODE_FIELD_NAME not in json: return None

        return NewInventoryItemMessage(
            json[NewInventoryItemMessage.ITEM_CODE_FIELD_NAME],
            json[NewInventoryItemMessage.ACTOR_CODE_FIELD_NAME])


    def create_update_inventory_item_message(self, json:dict) -> BorrowInventoryItemMessage | None:
        """Create BorrowInventoryItemMessage if json contains valid data
        Args:
            json (dict): data to create BorrowInventoryItemMessage
        Returns:
            BorrowInventoryItemMessage: if json args contain valid information to create BorrowInventoryItemMessage
            None: if json args does not contain valid information to create BorrowInventoryItemMessage
        """
        if BorrowInventoryItemMessage.UPDATE_TYPE_FIELD_NAME not in json: return None
        if BorrowInventoryItemMessage.BORROWER_CODE_FIELD_NAME not in json: return None
        if BorrowInventoryItemMessage.ITEM_CODE_FIELD_NAME not in json: return None
        if BorrowInventoryItemMessage.USER_CODE_FIELD_NAME not in json: return None

        return BorrowInventoryItemMessage(
            type=json[BorrowInventoryItemMessage.UPDATE_TYPE_FIELD_NAME],
            borrower_code=json[BorrowInventoryItemMessage.BORROWER_CODE_FIELD_NAME],
            item_code=json[BorrowInventoryItemMessage.ITEM_CODE_FIELD_NAME],
            user_code=json[BorrowInventoryItemMessage.USER_CODE_FIELD_NAME])