import boto3
from botocore.exceptions import ClientError

# boto3.setup_default_session(profile_name='default')

# dynamodb = boto3.resource('dynamodb')
# client = boto3.client('dynamodb')

# # def list_tables() -> list:
# #     response = client.list_tables()
# #     print(response['TableNames'])
# #     return response['TableNames']

from data_repositories import UserCredentialRepository

if __name__ == '__main__':
    repo = UserCredentialRepository()
    #repo.create_table_if_not_exists()
    #repo.delete_table(repo.TABLE_NAME)
    repo.get_table('user_credential')
    print(repo.get_table_list())

    table_exist = repo.table_exists('user_credential')
    print(f'Table [user_credential] exists: ', table_exist)

    