class Message(object):
    pass

class CreateUserCredentialMessage(Message):
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password

class UserCredentialPasswordUpdateMessage(Message):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

class LoginMessage(Message):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class UpdateUserCredentialMessage(Message):
    """NOT IN USE"""
    def __init__(self):
        pass