from datetime import datetime, timezone
from enum import Enum

from message_types import CreateUserCredentialMessage, UserCredentialPasswordUpdateMessage
from utility_types import PasswordUtility


class Record(object):
    pass

# UserCredential Records

class CredentialRecord(Record):
    def __init__(self):
        self.password_hash:str = None
        self.password_salt:str = None
        self.password_last_changed_datetime:datetime = None
        self.PasswordUtility = PasswordUtility()

    # def __get_salt_bytes(self, length=32):
    #     return secrets.token_bytes(length)
    #
    # def hash_password(self, password_text, salt_bytes = None):
    #     if salt_bytes is None:
    #         salt_bytes = self.__get_salt_bytes()
    #     password_bytes = password_text.encode('utf-8')
    #     combined_bytes = salt_bytes + password_bytes
    #     sha256 = hashlib.sha256()
    #     sha256.update(combined_bytes)
    #     return (sha256.hexdigest(), base64.b64encode(salt_bytes).decode())


class UserCredentialRecord(CredentialRecord):
    def __init__(self, record:dict = None ):
        super().__init__()
        self.username:str = None
        self.last_successful_login:datetime = None
        self.last_login_attempt_datetime:datetime = None
        self.failed_login_attempts:int = None
        self.status:UserCredentialRecord.Status = UserCredentialRecord.Status.NEW
        if record is not None:
            self.load_values(record)

    def __str__(self):
        return ','.join(f'{key}={value}' for key, value in self.__dict__.items())

    def load_values(self, record:dict):
        for key, value in record.items():
            setattr(self, key, value.popitem()[1])
            # print(f'Key = {key} and Value = {value.popitem()[1]}')
        #print(self)

    # class Field(Enum):
    #     USERNAME = 'username'
    #     PASSWORD_HASH = 'password_hash'
    #     PASSWORD_SALT = 'password_salt'
    #     PASSWORD_LAST_CHANGED_DATETIME = 'password_last_changed_datetime'
    #     LAST_SUCCESSFUL_LOGIN = 'last_successful_login'
    #     LAST_LOGIN_ATTEMPT_DATETIME = 'last_login_attempt_datetime'
    #     FAILED_LOGIN_ATTEMPTS = 'failed_login_attempts'
    #     STATUS = 'status'

    class Status(Enum):
        NEW = 'NEW1'
        ACTIVE = 'ACTIVE1'
        INACTIVE = 'INACTIVE1'
        def __str__(self) -> str:
            return self.name
        def __repr__(self) -> str:
            return self.name

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
        item = {}
        item['username'] = { 'NULL': True } if self.username is None else { 'S' : self.username }
        item['password_hash'] = {'NULL': True} if self.password_hash is None else {'S': self.password_hash}
        item['password_salt'] = {'NULL': True} if self.password_salt is None else {'S': self.password_salt}
        item['password_last_changed_datetime'] = {'NULL': True} if self.password_last_changed_datetime is None else {'S': self.password_last_changed_datetime}
        item['last_successful_login'] = {'NULL': True} if self.last_successful_login is None else {'S': self.last_successful_login}
        item['last_login_attempt_datetime'] = {'NULL': True} if self.last_login_attempt_datetime is None else {'S': self.last_login_attempt_datetime}
        item['failed_login_attempts'] = {'N': '0'} if self.failed_login_attempts is None else {'N': str(self.failed_login_attempts)}
        item['status'] = {'NULL': True} if self.status is None else {'S': str(self.status)}
        return item


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
