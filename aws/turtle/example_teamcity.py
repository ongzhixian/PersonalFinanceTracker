import os
import json
import requests
import pdb

def get_access_token():
    secret_id = 'dev'
    secrets_file_path = os.path.expandvars(f'%APPDATA%\\Microsoft\\UserSecrets\\{secret_id}\\teamcity.json')
    with open(secrets_file_path, 'r', encoding='utf8') as f:
        secrets = json.load(f)
        return secrets['access_key']

def get_teamcity_api_base_url(use_localhost_teamcity:bool = False):
    return 'http://localhost:8111' if use_localhost_teamcity else 'http://teamcity.mlp.com'


class TeamcityApi(object):
    def __init__(self, teamcity_base_url:str):
        teamcity_access_key = get_access_token()
        self.api_base_url = teamcity_base_url
        self.request_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json',
            'Authorization': f'Bearer {teamcity_access_key}'
        }

        # build_type_id = "CTQETreasuryE2eTests_PublishArtifacts"
        # parameters_api_url = f'{teamcity_base_url}/app/rest/buildTypes/id:{build_type_id}/parameters'
        # endpoint_url = f'{self.api_base_url}/app/rest/health'
        # response = requests.get(endpoint_url, headers=self.request_headers)
    
    def get_health(self):
        endpoint_url = f'{self.api_base_url}/app/rest/health'
        response = requests.get(endpoint_url, headers=self.request_headers)
        if response.ok:
            response_json = response.json()
            print('response_json', response_json)
            # for project in response_json:
            #     print(f"{project['name']:<30} ({project['shortName']})")

    def get_projects(self):
        endpoint_url = f'{self.api_base_url}/app/rest/projects?locator=parentProject:core'
        response = requests.get(endpoint_url, headers=self.request_headers)
        if response.ok:
            response_json = response.json()
            json.dump(response_json, open('mlp_example_teamcity_response.json', 'w', encoding='utf8'), indent=4)

    def get_project(self, projectId:str):
        endpoint_url = f'{self.api_base_url}/app/rest/projects/id:{projectId}'
        response = requests.get(endpoint_url, headers=self.request_headers)
        if response.ok:
            response_json = response.json()
            json.dump(response_json, open('mlp_example_teamcity_project_response.json', 'w', encoding='utf8'), indent=4)
        else:
            print('Response not OK:', response.status_code, response.text)

    def get_build(self, projectId:str):
        endpoint_url = f'{self.api_base_url}//app/rest/builds/project:{projectId}'
        response = requests.get(endpoint_url, headers=self.request_headers)
        if response.ok:
            response_json = response.json()
            json.dump(response_json, open('mlp_example_teamcity_build_response.json', 'w', encoding='utf8'), indent=4)
        else:
            print('Response not OK:', response.status_code, response.text)

    def get_builds_by_branch_name(self, branch_name:str):
        endpoint_url = f'{self.api_base_url}/app/rest/builds?locator=branch:{branch_name}'
        response = requests.get(endpoint_url, headers=self.request_headers)
        if response.ok:
            response_json = response.json()
            json.dump(response_json, open('mlp_example_teamcity_build_response.json', 'w', encoding='utf8'), indent=4)
        else:
            print('Response not OK:', response.status_code, response.text)

    def start_build(self, build_type_id:str, branch_name:str):
        endpoint_url = f'{self.api_base_url}/app/rest/buildQueue'
        payload = {
            "buildType": {
                "id": "CoreAthena_Release"
            },
            "branch": {
                "name": "2046/merge"
            }
        }
        response = requests.post(endpoint_url, headers=self.request_headers, json=payload)
        if response.ok:
            response_json = response.json()
            print('Build started successfully:', response_json)
            json.dump(response_json, open('mlp_example_teamcity_start_build_response.json', 'w', encoding='utf8'), indent=4)
        else:
            print('Response not OK:', response.status_code, response.text)


def main():
    teamcity_base_url = get_teamcity_api_base_url()
    teamcity_api = TeamcityApi(teamcity_base_url)
    #teamcity_api.get_health()
    # teamcity_api.get_projects()
    # teamcity_api.get_project('CoreAthena')
    # teamcity_api.get_build('CoreAthena')
    # teamcity_api.get_builds_by_branch_name('2046/merge')


if __name__ == "__main__":
    main()