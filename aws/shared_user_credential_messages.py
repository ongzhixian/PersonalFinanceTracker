"""Module for handling user_credential messages
Messages:
    AddUserCredentialMessage
    AuthenticateUserCredentialMessage
    UpdateUserCredentialPasswordMessage
"""

from shared_messages import Message

class AddUserCredentialMessage(Message):
    """Message for adding a user credential record
    """
    # Field names
    USERNAME_FIELD_NAME = 'username'
    PASSWORD_FIELD_NAME = 'password'

    def __init__(self, username:str, password:str):
        """
        Args:
            username (str):
                Username for user credential object
            password (str):
                Password for user credential
        Returns:
            None
        """
        self.username = username
        self.password = password


    @staticmethod
    def create_from_dict(json: dict):
        """Create AddUserCredentialMessage if json contains valid data
        Args:
            json (dict): data to create AddUserCredentialMessage
        Returns:
            AddUserCredentialMessage: if json args contain valid information to create AddUserCredentialMessage
            None: if json args does not contain valid information to create AddUserCredentialMessage
        """
        if AddUserCredentialMessage.USERNAME_FIELD_NAME not in json: return None
        if AddUserCredentialMessage.PASSWORD_FIELD_NAME not in json: return None

        return AddUserCredentialMessage(
            username=json[AddUserCredentialMessage.USERNAME_FIELD_NAME],
            password=json[AddUserCredentialMessage.PASSWORD_FIELD_NAME]
        )

    def __str__(self):
        return f"username: {self.username}"

class AuthenticateUserCredentialMessage(Message):
    """Message for authenticating a user credential record
    """
    # Field names
    USERNAME_FIELD_NAME = 'username'
    PASSWORD_FIELD_NAME = 'password'

    def __init__(self, username:str, password:str):
        """
        Args:
            username (str):
                Username for user credential object
            password (str):
                Password for user credential
        Returns:
            None
        """
        self.username = username
        self.password = password


    @staticmethod
    def create_from_dict(json: dict):
        """Create AuthenticateUserCredentialMessage if json contains valid data
        Args:
            json (dict): data to create AuthenticateUserCredentialMessage
        Returns:
            AuthenticateUserCredentialMessage: if json args contain valid information to create AuthenticateUserCredentialMessage
            None: if json args does not contain valid information to create AuthenticateUserCredentialMessage
        """
        if AuthenticateUserCredentialMessage.USERNAME_FIELD_NAME not in json: return None
        if AuthenticateUserCredentialMessage.PASSWORD_FIELD_NAME not in json: return None

        return AuthenticateUserCredentialMessage(
            username=json[AuthenticateUserCredentialMessage.USERNAME_FIELD_NAME],
            password=json[AuthenticateUserCredentialMessage.PASSWORD_FIELD_NAME]
        )

    def __str__(self):
        return f"username: {self.username}"

class UpdateUserCredentialPasswordMessage(Message):
    """Message for authenticating a user credential record
    """
    # Field names
    USERNAME_FIELD_NAME = 'username'
    PASSWORD_FIELD_NAME = 'password'

    def __init__(self, username:str, password:str):
        """
        Args:
            username (str):
                Username for user credential object
            password (str):
                Password for user credential
        Returns:
            None
        """
        self.username = username
        self.password = password


    @staticmethod
    def create_from_dict(json: dict):
        """Create UpdateUserCredentialPasswordMessage if json contains valid data
        Args:
            json (dict): data to create UpdateUserCredentialPasswordMessage
        Returns:
            UpdateUserCredentialPasswordMessage: if json args contain valid information to create UpdateUserCredentialPasswordMessage
            None: if json args does not contain valid information to create UpdateUserCredentialPasswordMessage
        """
        if UpdateUserCredentialPasswordMessage.USERNAME_FIELD_NAME not in json: return None
        if UpdateUserCredentialPasswordMessage.PASSWORD_FIELD_NAME not in json: return None

        return UpdateUserCredentialPasswordMessage(
            username=json[UpdateUserCredentialPasswordMessage.USERNAME_FIELD_NAME],
            password=json[UpdateUserCredentialPasswordMessage.PASSWORD_FIELD_NAME]
        )

    def __str__(self):
        return f"username: {self.username}"

