from ._base import BaseSearchAPI, BaseSeleniumAPI
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from ..data_lake.logger import log_io_to_json
import warnings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


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
        return jobs_html.find_all('li', recursive=False)
    

    def _next_page(self):
        """Paginate the results by clicking the "Show more jobs" button"""
        # Wait until the button is clickable
        wait = WebDriverWait(self.driver, 10)
        self.driver.execute_script("arguments[0].scrollIntoView();", self.driver.find_element(By.CSS_SELECTOR, 'button[data-test="load-more"]'))

        load_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="load-more"]')))
        self.driver.execute_script("arguments[0].scrollIntoView();", load_more_button)

        # Click the button
        load_more_button.click()

        time.sleep(5)

        try:
            close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.CloseButton')))
            close_button.click()
        except:
            # If the popup does not appear, continue without any action
            pass



    @log_io_to_json
    def fetch_job_listings(self, job_title: str, n_listings: int = 30, get_full_description: bool = False, close: bool = True):
        if get_full_description:
            warnings.warn("Fetching full job descriptions may trigger rate limiting or bot detection mechanisms on the Glassdoor server, potentially causing the process to fail.")

        self.search(job_title)
        time.sleep(10)

        job_postings_data = []
        job_listings = []

        while len(job_listings) < n_listings:
            job_listings = self._get_job_listings_from_search_results()
            if len(job_listings) < n_listings:
                try:
                    self._next_page()
                    time.sleep(5)
                except Exception as e:
                    warnings.warn(f"Failed to load more job listings. Error: {e}")
                    break

        

        for job in job_listings:
            company_name = job.find('span', class_=lambda x: x and x.startswith('EmployerProfile_compactEmployerName'))
            job_title = job.find('a', {'data-test': 'job-title'})
            location = job.find('div', {'data-test': 'emp-location'})
            salary = job.find('div', {'data-test': 'detailSalary'})
            snippet = job.find('div', {'data-test': 'descSnippet'})
            date = job.find('div', {'data-test': 'job-age'})
            link = job.find('a', {'data-test': 'job-title'})

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



