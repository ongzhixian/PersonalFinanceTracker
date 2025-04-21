from datetime import datetime, timezone

from message_types import CreateUserCredentialMessage

class Record(object):
    pass

# UserCredential Records

class UserCredentialRecord(Record):
    def __init__(self):
        self.username = None
        self.password_hash = None
        self.password_salt = None
        self.password_last_changed_datetime = None
        self.last_successful_login = None
        self.last_login_attempt_datetime = None
        self.failed_login_attempts = None
        self.status = None

class InsertUserCredentialRecord(UserCredentialRecord):

    def __init__(self, message:CreateUserCredentialMessage):
        pass
        super().__init__()
        self.username = message.username
        (sha256_hex, salt_b64) = self.repo.hash_password(message.password)
        self.password_hash = sha256_hex
        self.password_salt = salt_b64
        self.password_last_changed_datetime = datetime.now(timezone.utc).isoformat()


