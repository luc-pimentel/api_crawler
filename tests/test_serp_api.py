import pytest
from api_crawler import GoogleTrends, TrendingNow, GoogleJobs


@pytest.fixture
def google_trends():
    return GoogleTrends()


@pytest.fixture
def trending_now():
    return TrendingNow()

@pytest.fixture
def google_jobs():
    return GoogleJobs()



def test_google_trends_get(google_trends):
    # Arrange
    search_query = "Artificial Intelligence"

    # Act
    response = google_trends.get(search_query)

    # Assert
    assert isinstance(response, dict), "Response is not a dictionary"
    assert response['search_metadata']['status'] == 'Success', "Status is not Success"




def test_trending_now_get(trending_now):
    
    # Act
    response = trending_now.get()

    # Assert
    assert isinstance(response, dict), "Response is not a dictionary"
    assert response['search_metadata']['status'] == 'Success', "Status is not Success"




def test_google_jobs_search_job_postings(google_jobs):
    # Arrange
    job_title = "Data Analyst"

    # Act
    response = google_jobs.search_job_postings(job_title)

    # Assert
    assert isinstance(response, dict), "Response is not a dictionary"
    assert response['search_metadata']['status'] == 'Success', "Status is not Success"