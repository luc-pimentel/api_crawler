import requests
from decouple import config
from datetime import datetime, timedelta
from lake.logger import log_io_to_json
from .base import BaseSearchAPI, BaseRestfulAPI

GITHUB_API_KEY = config('GITHUB_API_KEY')


class GithubAPI(BaseRestfulAPI, BaseSearchAPI):
    def __init__(self):
        self.api_key = GITHUB_API_KEY
        self.base_url = 'https://api.github.com/'
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.api_key}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def get(self, endpoint:str, **kwargs):

        response = requests.get(self.base_url + endpoint,
                                headers = self.headers,
                                params = kwargs)
        return response
    
    def post(self):
        pass



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
        response = self.search_repositories(query, sort='stars', order='desc')

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
        response = self.search_repositories(query, sort='stars', order='desc')

        data = response.json()
        return data.get('items', [])