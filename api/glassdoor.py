from api.base import BaseSearchAPI, BaseAPI
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from lake.logger import log_io_to_json






class Glassdoor(BaseSearchAPI):
    def __init__(self, headless = True):
        self.base_url = "https://www.glassdoor.com/Job/"
        self.options = Options()
        
        if headless:
            self.options.add_argument('--headless')

        self.options.add_argument('--disable-gpu')
        self.options.add_argument("window-size=1200x600")
        self.options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
        self.driver = webdriver.Chrome(options = self.options)

    def search(self, job_title):
        job_query = job_title.replace(' ', '-').lower() + "-jobs-SRCH_KO0," + str(len(job_title)) + ".htm"
        search_url = self.base_url + job_query
        self.driver.get(search_url)
        return self.driver.page_source

    def scroll_to(self, xpath):
        self.driver.execute_script("arguments[0].scrollIntoView();", self.driver.find_element(By.XPATH,xpath))


    def close(self):
        self.driver.quit()
        


    @log_io_to_json
    def fetch_job_listings(self, job_title, n_listings: int = 10, get_full_description = False, close = True):

        if n_listings > 30:
            print("Warning: Requested number of listings exceeds 30. Pagination may be needed, but no pagination handling has been implemented yet.")

        def _get_company_name(base_xpath):
            try:
                return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[1]/div[1]/div[2]/span').text
            except NoSuchElementException:
                return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[1]/div[1]/div/span').text
        
        def _get_job_posting_title(base_xpath):
            return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[1]/a[1]').text

        def _get_job_posting_location(base_xpath):
            return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[1]/div[2]').text
        
        def _get_job_posting_salary(base_xpath):
            return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[1]/div[3]').text
        
        def _get_job_posting_skills(base_xpath):
            try:
                return self.driver.find_element(By.XPATH, f'{base_xpath}/div/div/div[1]/div[1]/div[4]/div[2]').text
            except NoSuchElementException as e:
                try:
                    return self.driver.find_element(By.XPATH, f'{base_xpath}/div/div/div[1]/div[1]/div[5]/div[2]').text
                except:
                    return None
        
        def _get_job_posting_snippet(base_xpath):
            try:
                return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[1]/div[4]/div[1]').text
            except NoSuchElementException as e:
                return self.driver.find_element(By.XPATH, f'{base_xpath}/div/div/div[1]/div[1]/div[3]/div').text
        
        def get_job_posting_date(base_xpath):
            return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[2]').text
        
        def get_job_posting_link(base_xpath):
            return self.driver.find_element(By.XPATH,f'{base_xpath}/div/div/div[1]/div[1]/a[2]').get_attribute('href')
        
        def _get_job_posting_full_description(url):
            self.driver.get(url)

            show_more_button = self.driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/section/div[2]/div[2]/button")
            show_more_button.click()

            time.sleep(10)

            return self.driver.find_element(By.XPATH,f'/html/body/div[3]/div[1]/div[2]/div/div[1]/div/div[1]/div/section/div[2]/div[1]').text




        def get_job_posting_info(i):

            base_xpath = f'/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{i+1}]'

            self.scroll_to(base_xpath)

            job_posting_dict = {'company_name': _get_company_name(base_xpath),
                              'title': _get_job_posting_title(base_xpath),
                              'location': _get_job_posting_location(base_xpath),
                              'salary': _get_job_posting_salary(base_xpath),
                              'skills': _get_job_posting_skills(base_xpath),
                              'snippet': _get_job_posting_snippet(base_xpath),
                              'date': get_job_posting_date(base_xpath),
                              'link': get_job_posting_link(base_xpath)}
            
            return job_posting_dict
        

        self.search(job_title)

        # Assuming the page has already been loaded by the search method

        job_postings_data = []

        for i in range(n_listings):


            job_postings_data.append(get_job_posting_info(i))
        

        if get_full_description:
            for job_posting_dict in job_postings_data:
                job_posting_dict['full_description'] = _get_job_posting_full_description(job_posting_dict['link'])

        if close:
            self.close()


        return job_postings_data

    