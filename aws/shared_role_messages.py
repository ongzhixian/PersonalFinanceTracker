"""Module for handling role messages
Messages:
    AddRoleMessage
    AuthenticateUserCredentialMessage
    UpdateUserCredentialPasswordMessage
"""
from shared_messages import Message

class AddRoleMessage(Message):
    """Message for adding a role record
    """
    # Field names
    NAME_FIELD_NAME = 'name'
    DESCRIPTION_FIELD_NAME = 'description'

    def __init__(self, name:str, description:str):
        """
        Args:
            name (str):
                Name for role
            description (str):
                Description of role
        Returns:
            None
        """
        self.name = name
        self.description = description
