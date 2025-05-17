"""Module for handling messages
Sections:
    Message (object) classes
        1. NewInventoryItemMessage
        1. UpdateInventoryItemMessage
        1. SuccessBorrowMessage
    Message Service Class(es)
        1. HciMessageService
"""

from shared_messages import Message

# MESSAGE CLASSES

## OTHER MESSAGE CLASSES

class NewInventoryItemMessage(Message):
    """Message for creating a new inventory item
    """
    # Field names
    ITEM_CODE_FIELD_NAME = 'itemCode'
    USER_CODE_FIELD_NAME = 'userCode'

    def __init__(self, item_code:str, user_code:str):
        self.item_code = item_code
        self.user_code = user_code

    def __str__(self):
        return f"Item code:{self.item_code}"

class UpdateInventoryItemMessage(Message):
    """Message for a borrowing a new inventory item
        """
    # Field names
    UPDATE_TYPE_FIELD_NAME = 'updateType'
    BORROWER_CODE_FIELD_NAME = 'borrowerCode'
    ITEM_CODE_FIELD_NAME = 'itemCode'
    USER_CODE_FIELD_NAME = 'userCode'

    BORROW_MESSAGE_TYPE = 'BORROW'
    RETURN_MESSAGE_TYPE = 'RETURN'
    EXTEND_BORROW_PERIOD_MESSAGE_TYPE = 'EXTEND-BORROW-PERIOD'

    def __init__(self, update_type:str, borrower_code:str, item_code: str, user_code: str):
        self.update_type = update_type
        self.borrower_code = borrower_code
        self.item_code = item_code
        self.user_code = user_code

    def __str__(self):
        return f"Type: {self.update_type}, Borrower Code: {self.borrower_code}, Item code:{self.item_code}, User code: {self.user_code}"

    def is_borrow_message(self):
        return self.update_type == UpdateInventoryItemMessage.BORROW_MESSAGE_TYPE

    def is_return_message(self):
        return self.update_type == UpdateInventoryItemMessage.RETURN_MESSAGE_TYPE

    def is_extend_borrow_message(self):
        return self.update_type == UpdateInventoryItemMessage.EXTEND_BORROW_PERIOD_MESSAGE_TYPE

class SuccessBorrowMessage(dict):
    """Message of a successful borrowed inventory item
    """
    # Field names
    # '#BORROW_BY': 'borrow_by',
    # '#BORROW_DATETIME': 'borrow_datetime',
    # '#DUE_DATETIME': 'due_datetime',
    # '#RECORD_UPDATE_BY': 'record_update_by',
    # '#RECORD_UPDATE_DATETIME': 'record_update_datetime',
    ITEM_CODE_FIELD_NAME = 'itemCode'
    BORROW_BY_FIELD_NAME = 'borrowBy'
    BORROW_DATETIME_FIELD_NAME = 'borrowDateTime'
    DUE_DATETIME_FIELD_NAME = 'dueDateTime'
    RECORD_UPDATE_BY_FIELD_NAME = 'recordUpdateBy'
    RECORD_UPDATE_DATETIME_FIELD_NAME = 'recordUpdateDateTime'

    def __init__(self):
        super().__init__()
        # item_code:str, borrow_by:str, borrow_datetime:str, due_datetime:str, record_update_by:str, record_update_datetime:str
        # self.item_code = attr if 'item_code' in attr
        # self.borrow_by = borrow_by
        # self.borrow_datetime = borrow_datetime
        # self.due_datetime = due_datetime
        # self.record_update_by = record_update_by
        # self.record_update_datetime = record_update_datetime

    def __str__(self):
        return 'SuccessBorrowMessage'
        #return f"Item code:{self.item_code}"


# MESSAGE SERVICE CLASSES

class HciMessageService(object):
    """A service object for creating messages"""

    @staticmethod
    def create_new_inventory_item_message(json:dict) -> NewInventoryItemMessage | None:
        """Create NewInventoryItemMessage if json contains valid data
        Args:
            json (dict): data to create NewInventoryItemMessage
        Returns:
            NewInventoryItemMessage: if json args contain valid information to create NewInventoryItemMessage
            None: if json args does not contain valid information to create NewInventoryItemMessage
        """
        if NewInventoryItemMessage.ITEM_CODE_FIELD_NAME not in json: return None
        if NewInventoryItemMessage.USER_CODE_FIELD_NAME not in json: return None

        return NewInventoryItemMessage(
            json[NewInventoryItemMessage.ITEM_CODE_FIELD_NAME],
            json[NewInventoryItemMessage.USER_CODE_FIELD_NAME])


    @staticmethod
    def create_update_inventory_item_message(json:dict) -> UpdateInventoryItemMessage | None:
        """Create UpdateInventoryItemMessage if json contains valid data
        Args:
            json (dict): data to create UpdateInventoryItemMessage
        Returns:
            UpdateInventoryItemMessage: if json args contain valid information to create UpdateInventoryItemMessage
            None: if json args does not contain valid information to create UpdateInventoryItemMessage
        """
        if UpdateInventoryItemMessage.UPDATE_TYPE_FIELD_NAME not in json: return None
        #if UpdateInventoryItemMessage.BORROWER_CODE_FIELD_NAME not in json: return None
        if UpdateInventoryItemMessage.ITEM_CODE_FIELD_NAME not in json: return None
        if UpdateInventoryItemMessage.USER_CODE_FIELD_NAME not in json: return None

        return UpdateInventoryItemMessage(
            update_type=json[UpdateInventoryItemMessage.UPDATE_TYPE_FIELD_NAME],
            borrower_code=json[UpdateInventoryItemMessage.BORROWER_CODE_FIELD_NAME] if UpdateInventoryItemMessage.BORROWER_CODE_FIELD_NAME in json else None,
            item_code=json[UpdateInventoryItemMessage.ITEM_CODE_FIELD_NAME],
            user_code=json[UpdateInventoryItemMessage.USER_CODE_FIELD_NAME])