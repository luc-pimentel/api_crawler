import pytest
from api_crawler import BraveSearchAPI

@pytest.fixture
def brave_api():
    return BraveSearchAPI()

def test_search(brave_api):
    response = brave_api.search('Data Analyst')
    assert isinstance(response, list), "Response should be a list"
    assert len(response) > 0, "Response list should not be empty"
    assert all(key in item for key in ['title', 'link', 'snippet'] for item in response), f"Each item in the response should have a 'title', 'link', and 'snippet' key."