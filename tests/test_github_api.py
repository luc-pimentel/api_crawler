import pytest
from api_crawler import GithubAPI


test_repo = 'jxnl/instructor'


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





def test_get_repos_invalid_repo_name_raises_error(github_api):
    """Test if the _get_repos method raises an error when the repo_name is not in the correct format"""
    with pytest.raises(ValueError):
        github_api._get_repos('invalid_repo_name', 'issues')


def test_get_repo_comments(github_api):
    response = github_api.get_repo_comments(test_repo)
    response.raise_for_status()



def test_get_repo_commits(github_api):
    response = github_api.get_repo_commits(test_repo)
    response.raise_for_status()



def test_get_repo_issues(github_api):
    response = github_api.get_repo_issues(test_repo)
    response.raise_for_status()


def test_get_repo_pulls(github_api):
    response = github_api.get_repo_pulls(test_repo)
    response.raise_for_status()




## NOTE: If the following methods are not returning a list of dicts, it means the flow is broken somewhere.
# However, these tests do not check to see if indeed all the values are returned by checking if the lenght of the list is equal to the number of values.


def test_get_all_repo_pull_requests(github_api):
    response = github_api.get_all_repo_pull_requests(test_repo)

    ## NOTE: If the method is not returning a list of dicts, it means the flow is broken somewhere.
    # However, this test does not check to see if indeed all the pull requests are returned by checking if the lenght of the list is equal to the number of pull requests.
    assert isinstance(response, list), "Response should be a list"
    assert all(isinstance(item, dict) for item in response), "All items in the response should be dictionaries"



def test_get_all_repo_comments(github_api):

    response = github_api.get_all_repo_comments(test_repo)
    assert isinstance(response, list), "Response should be a list"
    assert all(isinstance(item, dict) for item in response), "All items in the response should be dictionaries"



def test_get_all_repo_commits(github_api):
    response = github_api.get_all_repo_commits(test_repo)
    assert isinstance(response, list), "Response should be a list"
    assert all(isinstance(item, dict) for item in response), "All items in the response should be dictionaries"


def test_get_all_repo_issues(github_api):
    response = github_api.get_all_repo_issues(test_repo)
    assert isinstance(response, list), "Response should be a list"
    assert all(isinstance(item, dict) for item in response), "All items in the response should be dictionaries"