from shared_configuration import ConfigurationRepository
from shared_role import RoleRepository
from shared_user_credential import UserCredentialRepository
from utility_types import TokenUtility


class SharedTokenService(object):
    def __init__(self):
        self.configuration_repository = ConfigurationRepository()
        # self.role_repository = RoleRepository()
        self.user_credential_repository = UserCredentialRepository()

    def get_secret_key_from_configuration(self, configuration_id='UCM_SECRETS'):
        operation_result_message = self.configuration_repository.get_configuration(configuration_id)
        if 'content' not in operation_result_message.data_object: return None
        content = operation_result_message.data_object['content']

        if 'authentication_token' not in content: return None
        authentication_token = content['authentication_token']

        if 'value' not in authentication_token: return None

        secret_key = authentication_token['value']
        return secret_key

    def generate_token(self, message: str = '', configuration_id: str = 'UCM_SECRETS'):
        secret_key = self.get_secret_key_from_configuration(configuration_id)
        token_utility = TokenUtility(secret_key)
        new_token = token_utility.generate_token(60 * 60, message)
        return new_token

    def verify_token(self, auth_token: str, configuration_id: str = 'UCM_SECRETS'):
        secret_key = self.get_secret_key_from_configuration(configuration_id)
        token_utility = TokenUtility(secret_key)
        return token_utility.verify_token(auth_token)

    def get_token_content(self, auth_token: str, configuration_id: str = 'UCM_SECRETS'):
        secret_key = self.get_secret_key_from_configuration(configuration_id)
        token_utility = TokenUtility(secret_key)
        return token_utility.get_token_content(auth_token)

    def verify_token_has_roles(self, auth_token: str, target_roles: list[str] = [],
                               configuration_id: str = 'UCM_SECRETS'):
        secret_key = self.get_secret_key_from_configuration(configuration_id)
        token_utility = TokenUtility(secret_key)
        if not token_utility.verify_token(auth_token):
            return False

        token_content = token_utility.get_token_content(auth_token)
        operation_result_message = self.user_credential_repository.get_user_credential(username=token_content)
        if not operation_result_message.is_success:
            return False

        user_roles = set(operation_result_message.data_object.get('roles', []))

        # This probably the most efficient way to check if any of the target roles exist in user_roles
        return any(role in user_roles for role in target_roles)


def main():
    shared_token_service = SharedTokenService()
    print("\nTesting SharedTokenService...")

    token = shared_token_service.generate_token(message='SomeUserId')
    print("\nGenerated Token:", token)

    verify_response = shared_token_service.verify_token(
        'MTc1MzI1OTcxMHx0ZXN0dXNlcjFNIgoqoSzKj60YLTczmmXvLZy0e-uOiefxZvkmr-Y7fQ==')
    print("\nVerify token:", verify_response)

    token_content = shared_token_service.get_token_content(token)
    print("\nToken content:", token_content)


if __name__ == '__main__':
    main()