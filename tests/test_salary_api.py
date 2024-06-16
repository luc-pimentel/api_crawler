import pytest
from api_crawler import SalaryAPI
from bs4 import BeautifulSoup



@pytest.fixture
def salary_api():
    return SalaryAPI()


def test_create_search_endpoint(salary_api):
    job_title = "Software Engineer"
    expected_endpoint = "/tools/salary-calculator/search?keyword=Software%20Engineer"
    assert salary_api.create_search_endpoint(job_title) == expected_endpoint


def test_search(salary_api):
    """Test to see if the search function returns a BeautifulSoup object.
    If the request is forbidden, the get function will ultimately raise an error, thus triggering the test to fail.
    At this point, we are only testing if the request is successful and not blocked.
    """
    job_title = "Software Engineer"
    result = salary_api.search(job_title)
    assert isinstance(result, BeautifulSoup)



def test_search_job_roles(salary_api):
    job_title = "Software Engineer"
    response = salary_api.search_job_roles(job_title)

    assert isinstance(response, list), f"Expected a list, got {type(response)}"
    assert len(response) > 0, f"Expected a list with at least one element, got {response}"
    assert isinstance(response[0], dict), f"Expected a dictionary, got {type(response[0])}"
    assert all(key in response[0] for key in ['title', 'link', 'alternative_job_titles', 'description']),\
        f"Expected a dictionary with keys 'title', 'link', 'alternative_job_titles', 'description', got {response[0].keys()}"
    


def test_get_job_details(salary_api):

    job_title = "Software Engineer i"

    response = salary_api.get_salaries_range(job_title)

    assert isinstance(response, dict)
    assert all(key in response for key in ['25%', '10%', '90%', '75%', '50%(Median)']),\
          f"Expected a dictionary with keys '25%', '10%', '90%', '75%', '50%(Median)', got {response.keys()}"
    