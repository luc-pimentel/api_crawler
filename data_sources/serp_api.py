import requests
from decouple import config
from ._base import BaseRestfulAPI
from ..data_lake.logger import log_io_to_json
import os
from ..exceptions import NoAPIKeyException

SERP_API_KEY = config("SERP_API_KEY", default = None)


class BaseSerpAPI(BaseRestfulAPI):
    base_url = f'https://serpapi.com/search'
    
    def __init__(self, engine: str, api_key: str = SERP_API_KEY):
        super().__init__()


        self.api_key = api_key

        if self.api_key is None:
            self.api_key = os.environ.get("SERP_API_KEY")
        
        if self.api_key is None:
            raise NoAPIKeyException("SERP API key provided. Some methods may not work.\nPlease set the SERP_API_KEY environment variable using os.environ['SERP_API_KEY'] or pass it to the object via the api_key parameter.")


        self.params = {
            "api_key": self.api_key,
            "engine": engine
        }


    def get(self,**kwargs):
        query_params = self.params.copy()

        if kwargs:
            query_params.update(kwargs)
        
        return super().get(params=query_params)
    

    def post(self):
        pass

class GoogleTrends(BaseSerpAPI):
    def __init__(self):
        super().__init__('google_trends')

    @log_io_to_json
    def get(self, search_query:str, data_type:str = 'TIMESERIES', **kwargs):

        valid_data_types = ["TIMESERIES","GEO_MAP","GEO_MAP_0",
                            "RELATED_TOPICS","RELATED_QUERIES"]

        if data_type not in valid_data_types:
            raise ValueError(f"Invalid data_type. Expected one of {valid_data_types}")

        return super().get(q = search_query, datatype = data_type, **kwargs).json()


class TrendingNow(BaseSerpAPI):
    def __init__(self):
        super().__init__('google_trends_trending_now')

    @log_io_to_json
    def get(self, **kwargs):
        return super().get(**kwargs).json()

    def post(self):
        pass


class GoogleJobs(BaseSerpAPI):
    def __init__(self):
        super().__init__(f'google_jobs')

    
    def get(self, search_query:str, **kwargs):
        return super().get(q = search_query, **kwargs)
    

    @log_io_to_json
    def search_job_postings(self, search_query: str, **kwargs):
        response = super().get(q=search_query, **kwargs)
        
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            error_message = f"Request failed with status code: {response.status_code}"
            return {"error": error_message}