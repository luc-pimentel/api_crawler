from ._base import BaseRestfulAPI
from bs4 import BeautifulSoup



class SalaryAPI(BaseRestfulAPI):
    base_url = "https://salary.com"
    
    def __init__(self):
        super().__init__()
        
    def get(self, endpoint):
        response = super().get(endpoint)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def create_search_endpoint(self, job_title: str):

        endpoint = f"/tools/salary-calculator/search?keyword={job_title.replace(' ', '%20')}"

        return endpoint

    def search(self, job_title: str):
        endpoint = self.create_search_endpoint(job_title)
        soup = self.get(endpoint)
        return soup


    def job_salaries_list(self, job_title: str):
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