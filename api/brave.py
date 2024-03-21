import json
from .base import BaseSearchAPI
from decouple import config
from lake.logger import log_io_to_json


BRAVE_API_KEY = config('BRAVE_API_KEY')



class Brave(BaseSearchAPI):
    def __init__(self):
        from langchain.tools import BraveSearch
        
        self.search_engine = BraveSearch
        self.api_key = BRAVE_API_KEY

    @log_io_to_json
    def search(self, search_term, **kwargs):
        brave_search = self.search_engine.from_api_key(api_key= self.api_key, **kwargs)
        search_results = brave_search.run(search_term)
        return json.loads(search_results)