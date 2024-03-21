from abc import ABC, abstractmethod


class BaseAPI(ABC):

    @abstractmethod
    def __init__():
        '''Initialize the API'''


class BaseSearchAPI(BaseAPI):
    @abstractmethod
    def search():
        '''Run the search query through the search engine API'''



class BaseRestfulAPI(BaseAPI):
    
    @abstractmethod
    def get():
        '''Get method of the Restful API'''

    @abstractmethod
    def post():
        '''Post method of the Restful API'''


