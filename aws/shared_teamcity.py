import os
import json
import requests

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


class TeamCityApi(object):
    def __init__(self, json_configuration):
        self.json_configuration = json_configuration
        teamcity_permanent_token = json_configuration.get_secret("teamcity-permanent-token")
        self.request_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json',
            'Authorization': f'Bearer {teamcity_permanent_token}'
        }
        self.api_base_url = 'http://localhost:8111'

    def get_health(self):
        endpoint_url = f'{self.api_base_url}/app/rest/health'
        response = requests.get(endpoint_url, headers=self.request_headers)
        if response.ok:
            response_json = response.json()
            print('response_json', response_json)
            # for project in response_json:
            #     print(f"{project['name']:<30} ({project['shortName']})")

def main():
    CONFIG_FILE_PATH = f'./shared_teamcity_config.json'
    json_configuration = JsonConfiguration(CONFIG_FILE_PATH)
    teamcity_api = TeamCityApi(json_configuration)
    teamcity_api.get_health()
    
    

if __name__ == "__main__":
    main()