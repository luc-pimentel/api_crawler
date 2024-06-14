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
from typing import Optional, Tuple



class Glassdoor(BaseSearchAPI, BaseSeleniumAPI):
    base_url: str = "https://www.glassdoor.com/Job/"



    @staticmethod
    def create_job_search_url(job_title: str, location:str = None, job_type: str = None,
                    remote: bool = False, days_ago: int = 0, easy_apply: bool = False, min_company_rating: int = 0, exp_level: str = None, salary_range: Optional[Tuple[int, int]] = None,
                    company_size: str = None):

        job_type_dict = {
            'full_time': 'CF3CP',
            'contract': 'NJXCK',
            'part_time': '75GKK',
            'temporary': '4HKF7',
            'permanent': '5QWDV'
        }

        company_size_dict = {
        '1-200': 1,
        '201-500': 2,
        '501-1000': 3,
        '1001-5000': 4,
        '5001+': 5}


        if salary_range is not None:
            if not isinstance(salary_range, tuple) or len(salary_range) != 2 or not all(isinstance(num, int) for num in salary_range):
                raise ValueError("salary_range must be a tuple of two integers")

        if job_type and job_type not in job_type_dict.keys():
            raise ValueError(f"Invalid job type {job_type}. Choose from 'full_time', 'contract', 'part_time', 'temporary', 'permanent'")
        
        if company_size and company_size not in company_size_dict.keys():
            raise ValueError(f"Invalid company size {company_size}. Choose from '1-200', '201-500', '501-1000', '1001-5000', '5001+'")
        
        valid_exp_levels = ['internship', 'entrylevel', 'midseniorlevel','director','executive']
        if exp_level and exp_level not in valid_exp_levels:
            raise ValueError(f"Invalid experience level {exp_level}. Choose from {', '.join(valid_exp_levels)}")

    

        url = Glassdoor.base_url

        if location:
            ## NOTE: Location filtering on glassdoor URL requires a GEO ID, which is not so straightforward to obtain.
            ## As such, the search will be limited to the United States for now.
            raise NotImplementedError("Glassdoor API does not support location filtering yet.")
            #url += location.replace(' ','-')+'-' if location else ''

        url += job_title.replace(' ', '-').lower() + "-jobs-SRCH_KO0," + str(len(job_title)) + ".htm"

        url += f'?jobTypeIndeed={job_type_dict.get(job_type)}' if job_type else ''

        url += '&remoteWorkType=1' if remote else ''

        url += f'&fromAge={days_ago}' if days_ago and days_ago != 0 else ''

        url += '&applicationType=1' if easy_apply else ''

        url += f'&minRating={min_company_rating}.0' if min_company_rating else ''

        url += f'maxSalary={salary_range[1]}&minSalary={salary_range[0]}' if salary_range else ''

        url += f'&seniorityType={exp_level}' if exp_level else ''

        url += f'&employerSizes={company_size_dict.get(company_size)}' if company_size else ''
        
        return url





    def search(self, job_title: str, **kwargs):
        search_url = Glassdoor.create_job_search_url(job_title, **kwargs)
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
    def get_job_postings_data(self, job_title: str, n_listings: int = 30, get_full_description: bool = False, close: bool = True, **kwargs):
        if get_full_description:
            warnings.warn("Fetching full job descriptions may trigger rate limiting or bot detection mechanisms on the Glassdoor server, potentially causing the process to fail.")

        self.search(job_title, **kwargs)
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
                    warnings.warn(f"Failed to load more job listings. This is to be expected if there are no more job listings to load.")
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
            job_posting_dict['link'] = link['href'].split('?')[0] if link else None

            job_postings_data.append(job_posting_dict)

        if get_full_description:
            for job_posting_dict in job_postings_data:
                job_posting_dict['full_description'] = self._get_job_posting_full_description(job_posting_dict['link'])

        if close:
            self.close()

        return job_postings_data



