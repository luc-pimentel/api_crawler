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

        if api_key is None:
            api_key = os.environ.get("GITHUB_API_KEY")
        
        if api_key is None:
            raise NoAPIKeyException("GITHUB API key provided. Please set the GITHUB_API_KEY environment variable using os.environ['GITHUB_API_KEY'] or pass it to the object via the api_key parameter.")

    

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