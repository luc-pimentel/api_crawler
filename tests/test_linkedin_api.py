import pytest
from api_crawler import LinkedInAPI
from bs4 import BeautifulSoup

@pytest.fixture
def linkedin_api():
    return LinkedInAPI()


def test_search(linkedin_api):
    response = linkedin_api.search('Data Analyst', location='New York', days_ago=7)
    assert isinstance(response, BeautifulSoup), "Response is not a BeautifulSoup object"

    
def test_get_job_postings_data(linkedin_api):
    n_listings = 5
    job_posting_data = linkedin_api.get_job_postings_data('Data Analyst', location='New York', n_listings=n_listings, days_ago=7)
    assert isinstance(job_posting_data, list), "Job posting data is not a list"
    assert len(job_posting_data) == n_listings, f"Job posting data list is not of length {n_listings}"
    for job in job_posting_data:
        assert isinstance(job, dict), "Job posting is not a dictionary"

        ## NOTE: If any part of the scraping function fails to retrieve the job posting data, it will inevitably return None in the dict, thus failing the test below
        assert all(job.get(key) is not None for key in ['title', 'company', 'location', 'time', 'link']), "Job posting has None values for required keys"