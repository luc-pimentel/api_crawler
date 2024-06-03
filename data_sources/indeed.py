from ._base import BaseSearchAPI, BaseSeleniumAPI
from ..data_lake.logger import log_io_to_json
import warnings
from bs4 import BeautifulSoup



class IndeedAPI(BaseSeleniumAPI, BaseSearchAPI):
    base_url = 'https://www.indeed.com'

    def __init__(self):
        super().__init__()

    def search(self, search_query: str, location: str = 'United States'):
        search_query = search_query.replace(' ', '+')
        location = location.replace(' ', '+')


        url = f'{self.base_url}/jobs?q={search_query}&l={location}'
        self.driver.get(url)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    @log_io_to_json
    def get_job_postings_data(self, search_query: str, location: str = 'United States', n_listings: int = 10, get_full_description: bool = False, close: bool = True):
        if n_listings > 18:
            warnings.warn("Requested number of listings exceeds 18. Pagination may be needed, but no pagination handling has been implemented yet.")
        
        
        soup = self.search(search_query, location)

        job_posting_feed = soup.find('div', id='mosaic-jobResults').find('ul')

        job_posts_list = job_posting_feed.find_all('li', recursive=False)


        job_postings_data = []

        for job in job_posts_list[:n_listings]:
            job_title = job.find('span')
            company_name = job.find('span', {'data-testid': 'company-name'})
            job_location = job.find('div', {'data-testid': 'text-location'})
            snippet = job.find('ul', {'style': lambda x: x and x.startswith('list-style')})
            date = job.find('span', {'data-testid': lambda x: x and x.startswith('myJobsStateDate')})
            link = job.find('a')

            
            job_dict = {
                'job_title': job_title.text if job_title else None,
                'company_name': company_name.text if company_name else None,
                'job_location': job_location.text if job_location else None,
                'snippet': snippet.text if snippet else None,
                'date': date.text if date else None,
                'link': f"{self.base_url}{link['href']}" if link else None
                }

            job_postings_data.append(job_dict)

        if get_full_description:
            raise NotImplementedError('get_full_description is not implemented yet.')
            #for job in job_postings_data:
             #   job['full_description'] = self.get_job_description(job['link'])


        if close:
            self.close()


        return job_postings_data

