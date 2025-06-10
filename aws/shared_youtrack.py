import json
import os

import requests

import pdb

class JsonConfiguration(object):
    def __init__(self, config_file_path: str):
        with open(config_file_path, 'r', encoding='utf8') as in_file:
            self.config = json.load(in_file)

    def get_secret(self, secret_key):
        secrets_file_path_setting_value = self.config['secrets']['file-path']
        secrets_file_secret_key = self.config['secrets'][secret_key]
        secrets_json_file_path = os.path.normpath(os.path.expandvars(secrets_file_path_setting_value))
        with open(secrets_json_file_path, 'r', encoding='utf8') as in_file:
            secrets_json = json.load(in_file)
            return secrets_json[secrets_file_secret_key]



class YoutrackApi(object):

    def __init__(self, json_configuration):
        self.json_configuration = json_configuration
        youtrack_permanent_token = json_configuration.get_secret("youtrack-token-secret-key")
        self.request_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json',
            'Authorization': f'Bearer {youtrack_permanent_token}'
        }
        self.api_base_url = 'https://zhixian.youtrack.cloud/api'

    def get_projects(self):
        # https://www.jetbrains.com/help/youtrack/devportal/resource-api-admin-projects.html
        # https://www.jetbrains.com/help/youtrack/devportal/api-entity-Project.html#-x35rkv_5
        # id,name,shortName,createdBy(login,name,id),leader(login,name,id)
        fields_query = ','.join(['id', 'name', 'shortName', 'createdBy(login,name,id)', 'leader(login,name,id)'])
        endpoint_url = f'{self.api_base_url}/admin/projects?fields={fields_query}'
        response = requests.get(endpoint_url, headers=self.request_headers)
        if response.ok:
            response_json = response.json()
            for project in response_json:
                print(f"{project['name']:<30} ({project['shortName']})")
        # print(response.json())
        # if response.ok:
        #     return {
        #         'statusCode': 200,
        #         'body': json.dumps('Message sent succeed')
        #     }
        #
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps('Message sent failed')
        # }

def main():
    CONFIG_FILE_PATH = f'./shared_youtrack_config.json'
    json_configuration = JsonConfiguration(CONFIG_FILE_PATH)
    youtrack_api = YoutrackApi(json_configuration)
    youtrack_api.get_projects()


if __name__ == "__main__":
    # asyncio.run(main())
    main()
