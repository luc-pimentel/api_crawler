from bs4 import BeautifulSoup
from ._base import BaseRestfulAPI
from ..data_lake.logger import log_io_to_json
import warnings




class LinkedInAPI(BaseRestfulAPI):
    base_url:str = 'https://www.linkedin.com'


    def __init__(self):
        super().__init__()  # Ensure to call the superclass initializer if needed
        
    @staticmethod
    def create_job_search_endpoint(search_query: str, location: str = 'United States', days_ago: int = None, job_type: str = None, work_type: str = None, exp_level: str = None, min_salary = None, **kwargs):
        
        work_type_dict = {
            'on_site': 1,
            'remote': 2,
            'hybrid': 3
        }

        exp_level_dict = {
        'internship': 1,
        'entry_level': 2,
        'associate': 3,
        'mid_senior_level': 4,
        'director': 5
        }

        min_salary_dict = {
        '40000': 1,
        '60000': 2,
        '80000': 3,
        '100000': 4,
        '120000': 5
        }


        if job_type and job_type not in ['full_time', 'part_time', 'temporary', 'contract', 'internship']:
            raise ValueError(f"Invalid job type {job_type}. Choose from 'full_time', 'part_time', 'temporary', 'contract', 'internship'.")
        
        if work_type and work_type not in work_type_dict.keys():
            raise ValueError(f"Invalid work type {work_type}. Choose from 'on_site', 'remote', 'hybrid'.")
        
        if exp_level and exp_level not in exp_level_dict.keys():
            raise ValueError(f"Invalid experience level {exp_level}. Choose from 'internship', 'entry_level', 'associate', 'mid_senior_level', 'director'.")
        
        if min_salary and str(min_salary) not in min_salary_dict.keys():
            raise ValueError(f"Invalid minimum salary {min_salary}. Choose from '40000', '60000', '80000', '100000', '120000' in order to fit with the LinkedIn search filters.")



        endpoint = '/jobs/'
        endpoint += search_query.replace(' ', '-') + '-jobs?'
        endpoint += f'position=1&pageNum=0&location={location.replace(" ", "%2C")}'
        
        endpoint += f'&f_TPR=r{days_ago*86400}' if days_ago is not None else ''
        endpoint += f'&f_JT={job_type[0].upper()}' if job_type is not None else ''
        endpoint += f'&f_WT={work_type_dict[work_type]}' if work_type is not None else ''
        endpoint += f'&f_E={exp_level_dict[exp_level]}' if exp_level is not None else ''
        endpoint += f'&f_SB2={min_salary_dict[str(min_salary)]}' if min_salary is not None else ''
        return endpoint


    def get(self, endpoint, **kwargs):
        response = super().get(endpoint, **kwargs)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    
    def search(self, search_query: str, **kwargs):
        endpoint = self.create_job_search_endpoint(search_query, **kwargs)
        soup = self.get(endpoint)
        return soup


    @log_io_to_json
    def get_job_postings_data(self, search_query: str, **kwargs):
        soup = self.search(search_query, **kwargs)
        results_list = soup.find('ul', class_='jobs-search__results-list')


        job_listings = []
        for job in results_list.find_all('li'):
            title = job.find('h3', class_='base-search-card__title')
            subtitle = job.find('h4', class_='base-search-card__subtitle')
            location = job.find('span', class_='job-search-card__location')
            time_element = job.find('time')
            link = job.find('a', class_='base-card__full-link')
            job_listings.append({
                        'title': title.get_text(strip=True) if title else None,
                        'subtitle': subtitle.get_text(strip=True) if subtitle else None,
                        'location': location.get_text(strip=True) if location else None,
                        'link': link['href'] if link else None,
                        'list_date': time_element.get('datetime') if time_element else None
                    })

        return job_listings