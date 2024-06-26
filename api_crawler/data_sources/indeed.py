from ._base import BaseSearchAPI, BaseSeleniumAPI
from ..data_lake.logger import log_io_to_json
import warnings
from bs4 import BeautifulSoup
import time
from ..exceptions import *


class IndeedAPI(BaseSeleniumAPI, BaseSearchAPI):
    base_url = 'https://www.indeed.com'

    def __init__(self):
        super().__init__()


    @staticmethod
    def create_job_search_url(search_query, location = 'United States', start_from=0, days_ago=0, pay: int = None, exp_level: str = None, work_type: str = None, job_type: str = None):
        if days_ago not in [0, 1, 3, 7, 14]:
            warnings.warn("Due to how Indeed handles the date filter, the date_filter parameter might not be effective unless set to 1, 3, 7, or 14 days ago.")

        
        url = f"https://www.indeed.com/jobs?q={search_query.replace(' ', '+')}"
        url += f"+${pay:,}" if pay else ''
        url += f"&l={location.replace(' ', '+')}" if location else ''
        url += f"&start={start_from}" if start_from != 0 else ''
        url += f"&fromage={days_ago}" if days_ago != 0 else ''

        
        sc_parameters = [exp_level, work_type, job_type]

        url += "&sc=0kf%3A" if any(sc_parameters) else ''
        
        
        if exp_level:
            valid_levels = ['mid_level', 'entry_level', 'senior_level', 'no_exp']
            if exp_level not in valid_levels:
                raise ValueError(f"Invalid experience level: {exp_level}. Valid options are {valid_levels}")
                
            if exp_level == 'no_exp':
                url += "attr(D7S5D)"
            else:
                url += f"explvl({exp_level.upper()})"


        if job_type:
            valid_job_types = ['fulltime', 'parttime', 'internship', 'temporary', 'contract']
            if job_type not in valid_job_types:
                raise ValueError(f"Invalid job type: {job_type}. Valid options are {valid_job_types}")
            url += f"jt({job_type})"
        
        
        if work_type:
            valid_work_types = ['hybrid', 'remote']
            if work_type not in valid_work_types:
                raise ValueError(f"Invalid work type: {work_type}. Valid options are {valid_work_types}")
            if work_type == 'hybrid':
                url += "attr(PAXZC)"
            elif work_type == 'remote':
                url += "attr(DSQF7)"

        url += "%3B" if any(sc_parameters) else ''
        
        
        return url


    def search(self, search_query: str, location: str = 'United States', start_from: int = 0, **kwargs):
        """
        Performs a search on Indeed.com for job postings based on a given query and location.

        Args:
            search_query (str): The search term for job titles or keywords.
            location (str, optional): The geographical area to filter job postings. Defaults to 'United States'.
            start_from (int, optional): The starting index for job listings to handle pagination. 
                                        Ideally, it should be a multiple of 15, with 0 indicating the first page. 
                                        Defaults to 0.

        Returns:
            BeautifulSoup: A BeautifulSoup object containing the parsed HTML of the job search results page.

        Note:
            The 'start_from' parameter simulates pagination by adjusting the starting point of the job listings.
            Each increment by 15 represents moving to the next page of results.
        """

        url = self.create_job_search_url(search_query, location, start_from, **kwargs)
        self.driver.get(url)

        if any(phrase in self.driver.page_source for phrase in [
            "Verify you are human by completing the action below",
            "Verifying you are human. This may take a few seconds.",
            "needs to review the security of your connection before proceeding."]):

            raise CaptchaException("CAPTCHA encountered while accessing Indeed.")

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        return soup
    

    def _extract_job_data(self, job):
        """
        Extracts job data from a single job posting HTML element.

        Args:
            job (bs4.element.Tag): A BeautifulSoup Tag object representing a single job posting.

        Returns:
            dict: A dictionary containing extracted data about the job posting, including:
                - job_title (str): The title of the job.
                - company_name (str): The name of the company posting the job.
                - job_location (str): The location of the job.
                - snippet (str): A short description or snippet of the job posting.
                - date (str): The date the job was posted or last updated.
                - link (str): A URL link to the full job posting.

        Note:
            - The function uses BeautifulSoup's `find` method to locate specific elements within the job posting HTML.
            - It handles cases where certain data might not be present by checking if the elements exist before attempting to access their text.
            - The link to the job posting is constructed by appending the relative link found in the HTML to the base URL of Indeed.
        """
        job_title = job.find('span')
        company_name = job.find('span', {'data-testid': 'company-name'})
        job_location = job.find('div', {'data-testid': 'text-location'})
        snippet = job.find('ul', {'style': lambda x: x and x.startswith('list-style')})
        date = job.find('span', {'data-testid': lambda x: x and x.startswith('myJobsStateDate')})
        link = job.find('a')

        job_dict = {
            'title': job_title.text if job_title else None,
            'company': company_name.text if company_name else None,
            'location': job_location.text if job_location else None,
            'snippet': snippet.text if snippet else None,
            'date': date.text if date else None,
            'link': f"{self.base_url}{link['href']}" if link else None
        }
        return job_dict
    


    def _collect_job_postings(self, soup):
        """
        Collects job postings from a BeautifulSoup object representing a page of job search results.

        Args:
            soup (BeautifulSoup): A BeautifulSoup object of the Indeed job search results page.

        Returns:
            list: A list of dictionaries, each containing data about a single job posting.

        Note:
            - This method specifically looks for a 'div' with an id of 'mosaic-jobResults' and then finds a 'ul' within it.
            - It assumes that each job posting is contained within an 'li' element directly under this 'ul'.
            - The method iterates over each 'li' element, extracting job data using the `_extract_job_data` method.
            - It handles the structure of the Indeed page as observed at the time of implementation, which may change in the future.
        """
        

        search_results = soup.find('div', id='mosaic-jobResults')

        if not search_results:
            raise NoResultsException("No search results found.")

        job_posting_feed = search_results.find('ul')

        job_posts_list = job_posting_feed.find_all('li', recursive=False)

        



        job_postings_data = []
        for job in job_posts_list:
            job_postings_data.append(self._extract_job_data(job))
        return job_postings_data
    

    def _get_full_job_description(self, url:str):

        self.driver.get(url)

        page_source  = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        ### TODO: Check for captcha and throw an error if it is detected

        job_description_tab = soup.find('div', id = 'jobDescriptionText')

        full_job_description = job_description_tab.text.strip() if job_description_tab else None

        return full_job_description



    @log_io_to_json
    def get_job_postings_data(self, search_query: str, location: str = 'United States', n_listings: int = 15, get_full_description: bool = False, close: bool = True, **kwargs):
        """
        Retrieves a specified number of job postings from Indeed based on the search query and location.

        Args:
            search_query (str): The search term for job titles or keywords.
            location (str, optional): The geographical area to filter job postings. Defaults to 'United States'.
            n_listings (int, optional): The number of job postings to retrieve. Defaults to 15.
            get_full_description (bool, optional): If True, retrieves full job descriptions. Not implemented yet. Defaults to False.
            close (bool, optional): If True, closes the Selenium WebDriver after fetching the data. Defaults to True.

        Raises:
            NotImplementedError: If `get_full_description` is True, as this feature is not implemented.

        Returns:
            list: A list of dictionaries, each representing a job posting with details such as job title, company name, location, snippet, date, and link.

        Notes:
            - This function uses pagination to fetch multiple pages if `n_listings` exceeds 15, which may trigger captchas or rate limits.
            - The function logs input and output data to JSON as part of its operation due to the `log_io_to_json` decorator.
        """
        if get_full_description:
            warnings.warn('Using the parameter get_full_description = True may trigger captchas or rate limits.')
        
        
        if n_listings > 15:
            warnings.warn('Pagination will be used for n_listing > 15. This can trigger captchas and rate limits.')



        job_postings_data = []
        current_start = 0


        while len(job_postings_data) < n_listings:
            soup = self.search(search_query, location, start_from=current_start, **kwargs)
                
            page_job_postings = self._collect_job_postings(soup)
            job_postings_data.extend(page_job_postings)
            
            
            current_start += 15  # Move to the next page

        if get_full_description:
            for job in job_postings_data:
                job['full_description'] = self._get_full_job_description(job['link']) if job.get('link') else None

        if close:
            self.close()

        return job_postings_data[:n_listings]

