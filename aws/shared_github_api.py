import os
import json
import re
import requests

import pdb

class GithubApi(object):
    GITHUB_TOKEN_SECRET_NAME = 'github_localhost_app_token'
    GITHUB_API_BASE_URL = 'https://api.github.com'
    GITHUB_PAGINATION_REGEX = re.compile(r"\<(?P<url>http[\S]*)\>;\s+rel=\"(?P<relationship>\w+)\"")
    
    def __init__(self, username):
        app_secrets = self._get_secrets_dict()
        github_token =  app_secrets[GithubApi.GITHUB_TOKEN_SECRET_NAME] if GithubApi.GITHUB_TOKEN_SECRET_NAME in  app_secrets else None
        if github_token is None:
            raise RuntimeError('Missing secret: github_localhost_app_token')
        self.request_headers = {
            'Content-Type': 'application/vnd.github+json; charset=utf-8',
            'X-GitHub-Api-Version': '2022-11-28',
            'Authorization': f'Bearer {github_token}'
        }
        
        
        self.username = username

    def _get_secrets_dict(self) -> dict:
        app_secrets = {}
        user_secrets_id = 'tech-notes-press'
        user_secrets_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/secrets-development.json')
        with open(user_secrets_path) as input_file:
            all_secrets = json.load(input_file)
            if GithubApi.GITHUB_TOKEN_SECRET_NAME in all_secrets:
                app_secrets[GithubApi.GITHUB_TOKEN_SECRET_NAME] = all_secrets[GithubApi.GITHUB_TOKEN_SECRET_NAME]
        return app_secrets

    # def get_pagination_links(self, response_headers):
    #     link_header = response_headers['Link']  if 'Link' in response_headers else None
    #     print('link_header', link_header)
    #     if link_header is None:
    #         return None
        
    #     pagination_links = {}
    #     relation_links = link_header.split(',')
    #     print(relation_links)
    #     for relation_link in relation_links:
    #         relation_link_match = GithubApi.GITHUB_PAGINATION_REGEX.match(relation_link.strip())
    #         if relation_link_match is None:
    #             continue
    #         pagination_links[relation_link_match.group('relationship')] = relation_link_match.group('url')
    #     return pagination_links


    def _get_pagination_links(self, response_headers):
        link_header = response_headers.get('Link')

        pagination_links = {
            match.group('relationship'): match.group('url')
            for link in link_header.split(',')
            if (match := GithubApi.GITHUB_PAGINATION_REGEX.match(link.strip()))
        } if link_header else {}

        return pagination_links


    def xxlist_repositories(self):
        """List repositories for a user
        See: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user
        """
        repository_list = []
        endpoint_url = f'{GithubApi.GITHUB_API_BASE_URL}/users/{self.username}/repos'
        response = requests.get(endpoint_url, headers=self.request_headers)
        pagination_links = self._get_pagination_links(response.headers)
        repository_list.extend(response.json())
        
        while 'next' in pagination_links:
            next_page_url = pagination_links['next']
            response = requests.get(next_page_url, headers=self.request_headers)
            pagination_links = self._get_pagination_links(response.headers)
            repository_list.extend(response.json())

        return repository_list
        # print(pagination_links)
        repository_list = response.json()
        print(len(repository_list))

        with open('dmp.json', 'w', encoding='utf8') as out_file:
            out_file.write(json.dumps(repository_list))
        return repository_list
    
    def list_repositories(self):
        repository_list = []
        next_page_url = f'{GithubApi.GITHUB_API_BASE_URL}/users/{self.username}/repos'

        while next_page_url:
            response = requests.get(next_page_url, headers=self.request_headers)
            repository_list.extend(response.json())
            pagination_links = self._get_pagination_links(response.headers)
            next_page_url = pagination_links.get('next')  # Simplified pagination handling

        return repository_list


if __name__ == "__main__":
    github_api = GithubApi('ongzhixian')
    repositories = github_api.list_repositories()
    print(len(repositories))
