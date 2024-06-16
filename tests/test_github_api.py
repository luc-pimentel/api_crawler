import pytest
from api_crawler import GithubAPI



@pytest.fixture
def github_api():
    return GithubAPI()


def test_search_repositories(github_api):
    response = github_api.search_repositories('Python')

    assert response.status_code == 200, "Response status code should be 200"

    # Check if the response contains 'items'
    items = response.json().get('items')
    assert items is not None, "'items' should be in the response"
    
    # Check if 'items' is a list
    assert isinstance(items, list), "'items' should be a list"
    
    # Optionally, check if the list is not empty
    assert len(items) > 0, "'items' list should not be empty"




def test_get_trending_repos(github_api):
    response = github_api.get_trending_repos('Python')
    
    assert isinstance(response, list), "Response should be a list"
    assert len(response) > 0, "Response should not be empty"

