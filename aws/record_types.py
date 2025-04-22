from datetime import datetime, timezone
from enum import Enum

from message_types import CreateUserCredentialMessage, UserCredentialPasswordUpdateMessage
from utility_types import PasswordUtility


class Record(object):
    pass

# UserCredential Records

class CredentialRecord(Record):
    def __init__(self):
        self.password_hash:str|None = None
        self.password_salt:str|None = None
        self.password_last_changed_datetime:datetime|None = None
        self.PasswordUtility = PasswordUtility()


class UserCredentialRecord(CredentialRecord):
    def __init__(self, record:dict = None ):
        super().__init__()
        self.username:str|None = None
        self.last_successful_login:datetime|None = None
        self.last_login_attempt_datetime:datetime|None = None
        self.failed_login_attempts:int = 0
        self.status:UserCredentialRecord.Status = UserCredentialRecord.Status.NEW
        if record is not None:
            self.load_values(record)

    def __str__(self):
        return ','.join(f'{key}={value}' for key, value in self.__dict__.items())

    def load_values(self, record:dict):
        for key, value in record.items():
            setattr(self, key, value.popitem()[1])

    class Status(Enum):
        NEW = 'NEW1'
        ACTIVE = 'ACTIVE1'
        INACTIVE = 'INACTIVE1'
        def __str__(self) -> str:
            return self.name
        def __repr__(self) -> str:
            return self.name

    # class Field(Enum):
    #     USERNAME = 'username'
    #     PASSWORD_HASH = 'password_hash'
    #     PASSWORD_SALT = 'password_salt'
    #     PASSWORD_LAST_CHANGED_DATETIME = 'password_last_changed_datetime'
    #     LAST_SUCCESSFUL_LOGIN = 'last_successful_login'
    #     LAST_LOGIN_ATTEMPT_DATETIME = 'last_login_attempt_datetime'
    #     FAILED_LOGIN_ATTEMPTS = 'failed_login_attempts'
    #     STATUS = 'status'


class InsertUserCredentialRecord(UserCredentialRecord):

    def __init__(self, message:CreateUserCredentialMessage):
        super().__init__()
        self.username = message.username
        (sha256_hex, salt_b64) = self.PasswordUtility.hash_password(message.password)
        self.password_hash = sha256_hex
        self.password_salt = salt_b64
        self.password_last_changed_datetime = datetime.now(timezone.utc).isoformat()
        self.last_successful_login = None
        self.last_login_attempt_datetime = None
        self.failed_login_attempts = 0
        self.status = UserCredentialRecord.Status.NEW

    def to_dynamodb_item(self):
        return {
            'username': {'NULL': True} if self.username is None else {'S': self.username},
            'password_hash': {'NULL': True} if self.password_hash is None else {'S': self.password_hash},
            'password_salt': {'NULL': True} if self.password_salt is None else {'S': self.password_salt},
            'password_last_changed_datetime': {'NULL': True} if self.password_last_changed_datetime is None else {'S': self.password_last_changed_datetime},
            'last_successful_login': {'NULL': True} if self.last_successful_login is None else {'S': self.last_successful_login},
            'last_login_attempt_datetime': {'NULL': True} if self.last_login_attempt_datetime is None else {'S': self.last_login_attempt_datetime},
            'failed_login_attempts': {'N': '0'} if self.failed_login_attempts is None else {'N': str(self.failed_login_attempts)},
            'status': {'NULL': True} if self.status is None else {'S': str(self.status)}
        }

class UpdateUserCredentialPasswordRecord(CredentialRecord):
    def __init__(self, message:UserCredentialPasswordUpdateMessage):
        super().__init__()
        self.username = message.username
        (sha256_hex, salt_b64) = self.PasswordUtility.hash_password(message.password)
        self.password_hash = sha256_hex
        self.password_salt = salt_b64
        self.password_last_changed_datetime = datetime.now(timezone.utc).isoformat()

    # def to_dynamodb_item(self):
    #     item = {}
    #     item['username'] = { 'NULL': True } if self.username is None else { 'S' : self.username }
    #     item['password_hash'] = {'NULL': True} if self.password_hash is None else {'S': self.password_hash}
    #     item['password_salt'] = {'NULL': True} if self.password_salt is None else {'S': self.password_salt}
    #     item['password_last_changed_datetime'] = {'NULL': True} if self.password_last_changed_datetime is None else {'S': self.password_last_changed_datetime}
    #     return item
