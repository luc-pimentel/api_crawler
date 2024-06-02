from ._base import BaseSearchAPI, BaseSeleniumAPI
import requests

from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from ..data_lake.logger import log_io_to_json
import warnings






class Glassdoor(BaseSearchAPI, BaseSeleniumAPI):
    base_url: str = "https://www.glassdoor.com/Job/"


    def search(self, job_title: str):
        job_query = job_title.replace(' ', '-').lower() + "-jobs-SRCH_KO0," + str(len(job_title)) + ".htm"
        search_url = self.base_url + job_query
        self.driver.get(search_url)
        return self.driver.page_source

    def _get_job_posting_full_description(self, url: str):

        self.driver.get(url)

        show_more_button = self.driver.find_element(By.XPATH, "//button[starts-with(@class, 'JobDetails_showMore__')]")
        show_more_button.click()

        time.sleep(10)

        page_source = self.driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        job_description_div = soup.find('div', class_=lambda x: x and x.startswith('JobDetails_jobDescription__'))

        time.sleep(10)

        return job_description_div.text if job_description_div else None


    def _get_job_listings_from_search_results(self):

        page_source = self.driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        jobs_html = soup.find('ul', {'aria-label': 'Jobs List'})

        # Print the BeautifulSoup object of the element
        return jobs_html.find_all('li')



    @log_io_to_json
    def fetch_job_listings(self, job_title: str, n_listings: int = 10, get_full_description: bool = False, close: bool = True):


        if n_listings > 30:
            warnings.warn("Requested number of listings exceeds 30. Pagination may be needed, but no pagination handling has been implemented yet.")

        if get_full_description:
            warnings.warn("Fetching full job descriptions may trigger rate limiting or bot detection mechanisms on the Glassdoor server, potentially causing the process to fail.")


        self.search(job_title)

        time.sleep(10)

        # Assuming the page has already been loaded by the search method

        job_listings = self._get_job_listings_from_search_results()


        job_postings_data = []

        for job in job_listings[:n_listings]:
            company_name = job.find('span', class_=lambda x: x and x.startswith('EmployerProfile_compactEmployerName'))
            job_title = job.find('a', {'data-test': 'job-title'})
            location = job.find('div', {'data-test': 'emp-location'})
            salary = job.find('div', {'data-test': 'detailSalary'})
            snippet = job.find('div', {'data-test': 'descSnippet'})
            date = job.find('div', {'data-test': 'job-age'})
            link = job.find('a', {'data-test': 'job-title'})

            
            # NOTE: Splitting up the logic to avoid errors when an element is not found
            elements = {
                'company_name': company_name,
                'title': job_title,
                'location': location,
                'salary': salary,
                'snippet': snippet,
                'date': date,
                'link': link
            }

            job_posting_dict = {key: (element.text if element else None) for key, element in elements.items()}
            job_posting_dict['link'] = link['href'] if link else None

            job_postings_data.append(job_posting_dict)
        

        if get_full_description:
            for job_posting_dict in job_postings_data:
                job_posting_dict['full_description'] = self._get_job_posting_full_description(job_posting_dict['link'])

        if close:
            self.close()


        return job_postings_data
