class Message(object):
    pass

class CredentialMessage(Message):
    """A CredentialMessage represents a message with following fields:
    1. username (str)
    2. password (str)
    """
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password

class CreateUserCredentialMessage(CredentialMessage):
    def __init__(self, username:str, password:str):
        super().__init__(username, password)

class UserCredentialPasswordUpdateMessage(CredentialMessage):
    def __init__(self, username: str, password: str):
        super().__init__(username, password)

class LoginMessage(CredentialMessage):
    def __init__(self, username: str, password: str):
        super().__init__(username, password)

#
# class UpdateUserCredentialMessage(Message):
#     """NOT IN USE"""
#     def __init__(self):
#         pass