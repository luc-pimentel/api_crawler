from bs4 import BeautifulSoup
from ._base import BaseRestfulAPI
from ..data_lake.logger import log_io_to_json





class LinkedInAPI(BaseRestfulAPI):
    
    def __init__(self):
        super().__init__()  # Ensure to call the superclass initializer if needed
        self.base_url = 'https://www.linkedin.com'

    def get(self, endpoint, **kwargs):
        response = super().get(endpoint, **kwargs)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def post(self, endpoint, data=None, **kwargs):
        # Construct the full URL
        url = f"{self.base_url}{endpoint}"
        # Assuming you have a session or similar to make requests
        response = self.session.post(url, data=data, **kwargs)
        return response

    def search(self, search_query: str, location: str = 'United States', **kwargs):
        search_query = search_query.replace(' ', '-')
        location = location.replace(' ', '%2C')
        endpoint = f'/jobs/{search_query}-jobs?position=1&pageNum=0&location={location}'
        soup = self.get(endpoint, **kwargs)
        return soup


    @log_io_to_json
    def get_job_postings_data(self, search_query: str, location: str = 'United States', **kwargs):
        soup = self.search(search_query, location, **kwargs)
        results_list = soup.find('ul', class_='jobs-search__results-list')

        job_listings = []
        for job in results_list.find_all('li'):
            title = job.find('h3', class_='base-search-card__title').get_text(strip=True)
            subtitle = job.find('h4', class_='base-search-card__subtitle').get_text(strip=True)
            location = job.find('span', class_='job-search-card__location').get_text(strip=True)
            time_element = job.find('time').get('datetime')
            link = job.find('a', class_='base-card__full-link')['href']
            job_listings.append({
                'title': title,
                'subtitle': subtitle,
                'location': location,
                'link': link,
                'list_date': time_element
            })

        return job_listings