from ._base import BaseSearchAPI
from GoogleNews import GoogleNews




class GoogleNewsAPI(BaseSearchAPI):
    def __init__(self, **kwargs):
        self.googlenews = GoogleNews(lang = 'en', region = 'US', **kwargs)

    def search(self, search_term: str):
        self.googlenews.search(search_term)

        results_list = self.googlenews.results()

        return results_list


    def clear_results(self):
        self.googlenews.clear()