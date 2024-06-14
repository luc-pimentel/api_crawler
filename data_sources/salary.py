from ._base import BaseRestfulAPI
from bs4 import BeautifulSoup
from ..data_lake.logger import log_io_to_json
import requests


class SalaryAPI(BaseRestfulAPI):
    base_url = "https://salary.com"

    

    
    def __init__(self):
        super().__init__()
        
    def get(self, endpoint):
        response = super().get(endpoint)
        try:
            response.raise_for_status()
        except Exception as e:
            return response
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup

    def create_search_endpoint(self, job_title: str):

        endpoint = f"/tools/salary-calculator/search?keyword={job_title.replace(' ', '%20')}"

        return endpoint

    def search(self, job_title: str):
        endpoint = self.create_search_endpoint(job_title)
        soup = self.get(endpoint)
        return soup

    @log_io_to_json
    def get_salaries_range(self, job_title: str):

        soup = self.get(f"/tools/salary-calculator/{job_title.lower().replace(' ', '-')}")
        

        if isinstance(soup, requests.Response):
            raise ValueError(f"Could not find salary details for '{job_title}'. Make sure the job title is accurate as listed on salary.com.")
        

        bellcurve = soup.find('g', attrs={'data-name': 'chart_desktop'})

        salary_ranges = bellcurve.find_all('g', id = lambda x: x and x.startswith('salary'), recursive=False)

        salaries_dict = {}

        for range in salary_ranges:
            results = results = range.find_all('text', attrs={'data-name': True}) + range.find_all('text', id='top_salary_value')

            percentile = results[0].text.strip()

            salary = results[1].text.strip() if len(results) > 1 else None

            salaries_dict[percentile] = salary

        return salaries_dict


    @log_io_to_json
    def search_job_roles(self, job_title: str):
        soup = self.search(job_title)


        search_results = soup.find('div', class_= 'sa-layout-section border-top-none sal-border-bottom')

        jobs_list = search_results.find_all('div', class_='sal-popluar-skills margin-top20', recursive=False)

        jobs_info_list = []

        for job in jobs_list:
            job_title = job.find('div', class_ = lambda x: x and x.endswith('sal-jobtitle'))
            link = job.find('a', class_ = lambda x: x and x.startswith('a-color'))
            alternative_job_titles = job.find('div', class_= lambda x: x and x.startswith('sal-font-subalttitle'))
            description = job.find('p', class_ = 'sal-jobdesc')

            job_dict = {'title':job_title.text.strip() if job_title else None,
                        'link': link.get('href') if link else None,
                        'alternative_job_titles': alternative_job_titles.text.strip() if alternative_job_titles else None,
                        'description': description.text.strip() if description else None}

            jobs_info_list.append(job_dict)


        return jobs_info_list