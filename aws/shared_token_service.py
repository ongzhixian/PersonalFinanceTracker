from shared_configuration import ConfigurationRepository
from utility_types import TokenUtility

class SharedTokenService(object):
    def __init__(self):
        self.configuration_repository = ConfigurationRepository()

    def get_secret_key_from_configuration(self, configuration_id='UCM_SECRETS'):
        operation_result_message = self.configuration_repository.get_configuration(configuration_id)
        if 'content' not in operation_result_message.data_object: return None
        content = operation_result_message.data_object['content']

        if 'authentication_token' not in content: return None
        authentication_token = content['authentication_token']

        if 'value' not in authentication_token: return None

        secret_key = authentication_token['value']
        return secret_key

    def generate_token(self, message: str = '', configuration_id:str = 'UCM_SECRETS'):
        secret_key = self.get_secret_key_from_configuration(configuration_id)
        token_utility = TokenUtility(secret_key)
        new_token = token_utility.generate_token(60 * 60, message)
        return new_token

    def verify_token(self, auth_token:str, configuration_id:str = 'UCM_SECRETS'):
        secret_key = self.get_secret_key_from_configuration(configuration_id)
        token_utility = TokenUtility(secret_key)
        return token_utility.verify_token(auth_token)

    def get_token_content(self, auth_token:str, configuration_id:str = 'UCM_SECRETS'):
        secret_key = self.get_secret_key_from_configuration(configuration_id)
        token_utility = TokenUtility(secret_key)
        return token_utility.get_token_content(auth_token)
