"""Module for handling role messages
Messages:
    AddRoleMessage
    AuthenticateUserCredentialMessage
    UpdateUserCredentialPasswordMessage
"""
import re
import stat
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

    @staticmethod
    def create_from_dict(json: dict):
        """Create AddRoleMessage if json contains valid data
        Args:
            json (dict): data to create AddRoleMessage
        Returns:
            AddRoleMessage: if json args contain valid information to create AddRoleMessage
            None: if json args does not contain valid information to create AddRoleMessage
        """
        if AddRoleMessage.NAME_FIELD_NAME not in json: return None
        if AddRoleMessage.DESCRIPTION_FIELD_NAME not in json: return None
        if AddRoleMessage.STATUS_FIELD_NAME not in json: return None

        return AddRoleMessage(
            name=json[AddRoleMessage.NAME_FIELD_NAME],
            description=json[AddRoleMessage.DESCRIPTION_FIELD_NAME],
            status=json[AddRoleMessage.STATUS_FIELD_NAME]
        )
