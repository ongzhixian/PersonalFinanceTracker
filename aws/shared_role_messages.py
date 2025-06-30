"""Module for handling role messages
Messages:
    AddRoleMessage
    AuthenticateUserCredentialMessage
    UpdateUserCredentialPasswordMessage
"""
import re
from shared_messages import Message

class AddRoleMessage(Message):
    """Message for adding a role record
    """
    # Field names
    NAME_FIELD_NAME = 'name'
    DESCRIPTION_FIELD_NAME = 'description'
    STATUS_FIELD_NAME = 'status'

    def __init__(self, name:str, description:str, status:str='active'):
        """
        Args:
            name (str):
                Name for role
            description (str):
                Description of role
        Returns:
            None
        """
        if not re.fullmatch(r'^\w+$', name):
            raise ValueError("name must only contain letters, digits, and underscores")
        self.name = name
        self.description = description
        self.status = status

    # def derive_key_from_name(self):
    #     """Convert name to a key suitable for use in a database
    #     Returns:
    #         str: Key representation of the name
    #     """
    #     return self.name.lower().replace(' ', '_')