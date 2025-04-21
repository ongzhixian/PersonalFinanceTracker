class Message(object):
    pass

class CreateUserCredentialMessage(Message):
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password