import pytest
from api_crawler import GoogleNewsAPI


@pytest.fixture
def google_news_api():
    return GoogleNewsAPI()

def test_search(google_news_api):

    response = google_news_api.search('Artificial Intelligence')
    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert all(key in response[0] for key in ['title','media','date','datetime','desc','link','img'])
