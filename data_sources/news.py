from ._base import BaseSearchAPI
from GoogleNews import GoogleNews




class NewsAPI(BaseSearchAPI):
    def __init__(self):
        self.newsapi = ''#NewsApiClient(api_key = news_api_key)

    def search(self, search_query: str, page_size: int = 10, language: str = 'en'):
        search_results = self.newsapi.get_everything(q = search_query, page_size = page_size, language = language)

        return search_results['articles']
    


class GoogleNewsAPI(BaseSearchAPI):
    def __init__(self, **kwargs):
        self.googlenews = GoogleNews(lang = 'en', region = 'US', **kwargs)

    def search(self, search_term: str):
        self.googlenews.search(search_term)

        results_list = self.googlenews.results()

        return results_list


    def clear_results(self):
        self.googlenews.clear()