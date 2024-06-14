from bs4 import BeautifulSoup
from ._base import BaseRestfulAPI
from ..data_lake.logger import log_io_to_json
import warnings
import time



class LinkedInAPI(BaseRestfulAPI):
    base_url:str = 'https://www.linkedin.com/'


    def __init__(self):
        super().__init__()
        
    @staticmethod
    def create_job_search_params(search_query: str, location: str = 'United States', start: int = 0, days_ago: int = None, job_type: str = None, work_type: str = None, exp_level: str = None, min_salary = None, **kwargs):
        
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

        params = {"keywords": search_query,
                  }

        params['location'] = location
        params['f_TPR'] = f'r{days_ago*86400}' if days_ago else None
        params['f_JT'] = job_type[0].upper() if job_type else None
        params['f_WT'] = work_type_dict[work_type] if work_type else None
        params['f_E'] = exp_level_dict[exp_level] if exp_level else None
        params['f_SB2'] = min_salary_dict[str(min_salary)] if min_salary else None
        params['start'] = start if start else 0

        # Remove None values from the dict
        params = {k: v for k, v in params.items() if v is not None}
        return params


    def get(self, endpoint, **kwargs):
        response = super().get(endpoint, **kwargs)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    
    def search(self, search_query: str, **kwargs):
    
        endpoint = 'jobs-guest/jobs/api/seeMoreJobPostings/search'
        params = self.create_job_search_params(search_query, **kwargs)

        soup = self.get(endpoint, params=params)
        return soup


    @log_io_to_json
    def get_job_postings_data(self, search_query: str, n_listings=10, **kwargs):
        job_listings = []
        start = 0

        while len(job_listings) < n_listings:
            soup = self.search(search_query, start=start, **kwargs)
            results_list = soup.find_all('li')

            if not results_list:
                break  # Exit if no more results are found

            for result in results_list:
                if len(job_listings) >= n_listings:
                    break  # Stop if we have enough listings

                title = result.find('h3', class_='base-search-card__title')
                company = result.find('h4', class_='base-search-card__subtitle')
                location = result.find('span', class_='job-search-card__location')
                time_element = result.find('time')
                link = result.find('a', class_='base-card__full-link')

                result_dict = {
                    'title': title.text.strip() if title else None,
                    'company': company.text.strip() if company else None,
                    'location': location.text.strip() if location else None,
                    'time': time_element.get('datetime') if time_element else None,
                    'link': link.get('href') if link else None
                }

                job_listings.append(result_dict)

            start += len(results_list)
            time.sleep(10)  # Move to the next page

        return job_listings