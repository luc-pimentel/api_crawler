import json
from ._base import BaseSearchAPI
from decouple import config
from ..data_lake.logger import log_io_to_json


BRAVE_API_KEY = config('BRAVE_API_KEY', default=None)



class BraveSearchAPI(BaseSearchAPI):
    def __init__(self):
        from langchain.tools import BraveSearch
        
        self.search_engine = BraveSearch

        if BRAVE_API_KEY is None:
            raise ValueError("BRAVE_API_KEY not found in the .env file. Please add it to proceed.")
        
        self.api_key = BRAVE_API_KEY


    @log_io_to_json
    def search(self, search_term: str, **kwargs):

        brave_search = self.search_engine.from_api_key(api_key= self.api_key, **kwargs)
        search_results = brave_search.run(search_term)
        
        return json.loads(search_results)