import json
import os
import requests
import pdb

def _get_teamcity_access_token():
    """Utility function to retrieve the TeamCity access token from a secrets file."""
    secrets_path = os.path.expandvars(f'%HOMEDRIVE%/notes/secrets/secrets.json')

    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Secrets file not found at {secrets_path}")

    with open(secrets_path, 'r', encoding='utf8') as in_file:
        secrets = json.load(in_file)
        return secrets.get("teamcity-access-token")

def get_build_parameters(teamcity_access_token: str):
    """Fetches build parameters from TeamCity for a specific build type."""
    teamcity_base_url = "http://teamcity.mlp.com"
    build_type_id = "CTQETreasuryE2eTests_PublishArtifacts"
    parameters_api_url = f'{teamcity_base_url}/app/rest/buildTypes/id:{build_type_id}/parameters'

    teamcity_request_headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {teamcity_access_token}'
    }

    response = requests.get(parameters_api_url, headers=teamcity_request_headers)
    response_json = response.json()
    with open('teamcity_parameters.json', 'w', encoding='utf8') as out_file:
        out_file.write(json.dumps(response_json, indent=4, ensure_ascii=False))
    return response_json

    #     self.request_headers = {
    #         'Content-Type': 'application/json; charset=utf-8',
    #         'Cache-Control': 'no-cache',
    #         'Accept': 'application/json',
    #         'Authorization': f'Bearer {youtrack_permanent_token}'
    #     }
    #     self.api_base_url = 'https://zhixian.youtrack.cloud/api'
    #
    # def get_projects(self):
    #     # https://www.jetbrains.com/help/youtrack/devportal/resource-api-admin-projects.html
    #     # https://www.jetbrains.com/help/youtrack/devportal/api-entity-Project.html#-x35rkv_5
    #     # id,name,shortName,createdBy(login,name,id),leader(login,name,id)
    #     fields_query = ','.join(['id', 'name', 'shortName', 'createdBy(login,name,id)', 'leader(login,name,id)'])
    #     endpoint_url = f'{self.api_base_url}/admin/projects?fields={fields_query}'
    #     response = requests.get(endpoint_url, headers=self.request_headers)
    #     if response.ok:
    #         response_json = response.json()
    #         for project in response_json:
    #             print(f"{project['name']:<30} ({project['shortName']})")
    #     # print(response.json())


def main():
    teamcity_access_token = _get_teamcity_access_token()
    parameters_json = get_build_parameters(teamcity_access_token)

    #
    property_list = parameters_json['property']
    feature_list = list(filter(lambda x: x['name'].startswith('env.FeatureList'), property_list))
    for index, feature in enumerate(feature_list):
        print(f"{index+1}: {feature['name']}")

    selected_feature = next(filter(lambda x: x['name'] == 'env.FeatureListTreasuryAthena', feature_list), None)
    if selected_feature is None:
        print("Selected feature not found.")
        return

    selected_feature_raw_value = selected_feature['type']['rawValue']
    import re
    pattern = r"data_\d+=['\u0027]([^'\u0027]+)['\u0027]"
    matches = re.findall(pattern, selected_feature_raw_value)
    pdb.set_trace()




if __name__ == '__main__':
    main()