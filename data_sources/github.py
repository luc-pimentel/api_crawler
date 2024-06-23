import requests
from decouple import config
from datetime import datetime, timedelta
from ..data_lake.logger import log_io_to_json
from ._base import BaseSearchAPI, BaseRestfulAPI
import os
from ..exceptions import NoAPIKeyException

GITHUB_API_KEY = config('GITHUB_API_KEY', default=None)


class GithubAPI(BaseRestfulAPI, BaseSearchAPI):
    def __init__(self, api_key: str = GITHUB_API_KEY):
        super().__init__()

        api_key = self._get_api_key(api_key, "GITHUB_API_KEY",
                                    message = """No API key found for Github API. Please set the GITHUB_API_KEY environment variable.
See how to get you API key by following this link: https://docs.github.com/en/rest/quickstart?apiVersion=2022-11-28&tool=curl""")
    
        self.api_key = api_key
        self.base_url = 'https://api.github.com/'
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.api_key}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def get(self, endpoint:str, **kwargs):
        '''Get method of the Restful API'''
        kwargs['headers'] = self.headers

        return super().get(endpoint, **kwargs)
    


    def _get_repos(self, repo_name:str, endpoint:str, **kwargs):

        if '/' not in repo_name or len(repo_name.split('/')) != 2:
            raise ValueError(f"repo_name must be in '{{owner}}/{{repo}}' format. Got {repo_name}")


        repo_endpoint = f'repos/{repo_name}/{endpoint}'
        return self.get(repo_endpoint, **kwargs)
    


    @log_io_to_json
    def get_repo_issues(self, repo_name:str, params = None, comments = False, **kwargs):
        if not comments:
            return self._get_repos(repo_name, 'issues', params = params, **kwargs).json()
        else:
            issues = self._get_repos(repo_name, 'issues', params = params, **kwargs).json()

            for issue in issues:
                issue['comments_thread'] = self._get_repos(repo_name, f'issues/{issue["number"]}/comments').json()
            return issues
    

    @log_io_to_json
    def get_all_repo_issues(self, repo, params = None, **kwargs):

        if params is None:
            params = {}

        all_issues = []
        page = 1
        while True:
            params = {'per_page': 100, 'page': page, **params}
            issues = self.get_repo_issues(repo, params=params, **kwargs).json()
            if len(issues) == 0:
                break
            all_issues.extend(issues)
            page += 1
        return all_issues


    
    @log_io_to_json
    def get_repo_pulls(self, repo_name: str, **kwargs):
        return self._get_repos(repo_name, 'pulls', **kwargs)
    
    
    @log_io_to_json
    def get_all_repo_pull_requests(self, repo, params = None, **kwargs):
        if params is None:
            params = {}

        all_pulls = []
        page = 1
        while True:
            params = {'per_page': 100, 'page': page, **params}
            pulls = self.get_repo_pulls(repo, params=params, **kwargs).json()
            if len(pulls) == 0:
                break
            all_pulls.extend(pulls)
            page += 1
        return all_pulls


    @log_io_to_json
    def get_repo_commits(self, repo_name: str, **kwargs):
        return self._get_repos(repo_name, 'commits', **kwargs)
    
    @log_io_to_json
    def get_all_repo_commits(self, repo, params = None, **kwargs):
        if params is None:
            params = {}

        all_commits = []
        page = 1
        while True:
            params = {'per_page': 100, 'page': page, **params}
            commits = self.get_repo_commits(repo, params=params, **kwargs).json()
            if len(commits) == 0:
                break
            all_commits.extend(commits)
            page += 1
        return all_commits
        

    @log_io_to_json
    def get_repo_comments(self, repo_name: str, **kwargs):
        return self._get_repos(repo_name, 'comments', **kwargs)

    @log_io_to_json
    def get_all_repo_comments(self, repo, params = None, **kwargs):
        if params is None:
            params = {}

        all_comments = []
        page = 1
        while True:
            params = {'per_page': 100, 'page': page, **params}
            comments = self.get_repo_comments(repo, params=params, **kwargs).json()
            if len(comments) == 0:
                break
            all_comments.extend(comments)
            page += 1
        return all_comments



    def search(self, endpoint, query, **kwargs):
        
        response = self.get(f"search/{endpoint}?q={query}", **kwargs)
        return response
        
    
    def search_repositories(self, query, **kwargs):

        response = self.search('repositories', query, **kwargs)
        return response



    @log_io_to_json
    def get_trending_repos(self, query:str, days:int =30):
        """
        Retrieves a list of trending Python repositories created within the last `days` days.

        Args:
            github_api (GithubAPI): An instance of the GithubAPI class.
            days (int, optional): The number of days to look back for new repositories. Defaults to 30.

        Returns:
            list: A list of dictionaries representing the trending Python repositories.
        """
        today = datetime.now()
        last_month = today - timedelta(days=days)
        last_month_str = last_month.strftime("%Y-%m-%d")

        query = f"{query} created:>{last_month_str}"
        response = self.search_repositories(query, params = {'sort':'stars', 'order':'desc'})

        data = response.json()
        return data.get('items', [])



    @log_io_to_json
    def get_trending_python_repos(self, days=30):
        """
        Retrieves a list of trending Python repositories created within the last `days` days.

        Args:
            github_api (GithubAPI): An instance of the GithubAPI class.
            days (int, optional): The number of days to look back for new repositories. Defaults to 30.

        Returns:
            list: A list of dictionaries representing the trending Python repositories.
        """
        today = datetime.now()
        last_month = today - timedelta(days=days)
        last_month_str = last_month.strftime("%Y-%m-%d")

        query = f"language:python created:>{last_month_str}"
        response = self.search_repositories(query, params = {'sort':'stars', 'order':'desc'})

        data = response.json()
        return data.get('items', [])