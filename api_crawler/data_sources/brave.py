import json
from ._base import BaseSearchAPI
from decouple import config
from ..data_lake.logger import log_io_to_json
from ..exceptions import NoAPIKeyException
import os

BRAVE_API_KEY = config('BRAVE_API_KEY', default=None)



class BraveSearchAPI(BaseSearchAPI):
    def __init__(self, api_key:str = BRAVE_API_KEY):
        from langchain.tools import BraveSearch
        
        self.search_engine = BraveSearch

        api_key = self._get_api_key(api_key, "BRAVE_API_KEY", message ="""Please set the BRAVE_API_KEY environment variable or pass it to the object via the api_key parameter.
You can get your API key here https://brave.com/search/api/""")
        
        self.api_key = api_key


    @log_io_to_json
    def search(self, search_term: str, **kwargs):

        brave_search = self.search_engine.from_api_key(api_key= self.api_key, **kwargs)
        search_results = brave_search.run(search_term)
        
        return json.loads(search_results)