import pytest
from api_crawler import IndeedAPI
from bs4 import BeautifulSoup


def test_search():

    response = IndeedAPI().search('Data Analyst', location='New York', days_ago=7)
    assert isinstance(response, BeautifulSoup), "Response is not a BeautifulSoup object"

    
def test_get_job_postings_data():
    indeed_api = IndeedAPI()
    n_listings = 5
    job_posting_data = indeed_api.get_job_postings_data('Data Analyst', location='New York', n_listings=n_listings, days_ago=7, get_full_description=True)
    assert isinstance(job_posting_data, list), "Job posting data is not a list"
    assert len(job_posting_data) == n_listings, f"Job posting data list is not of length {n_listings}"
    for job in job_posting_data:
        assert isinstance(job, dict), "Job posting is not a dictionary"

        ## NOTE: If any part of the scraping function fails to retrieve the job posting data, it will inevitably return None in the dict, thus failing the test below
        assert all(job.get(key) is not None for key in ['title', 'company', 'location', 'snippet', 'date', 'link', 'full_description']), f"Job posting has None values for required keys: {job}"