import requests
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

class BaseAPI(ABC):
    """
    Abstract base class for other API classes.
    It enforces the implementation of the __init__ method in subclasses.
    """

    @abstractmethod
    def __init__():
        '''Initialize the API'''





class BaseSearchAPI(BaseAPI):
    """
    Abstract base class for search engine API classes.
    
    This class enforces the implementation of the `search` method in subclasses,
    which should handle running search queries through the respective search engine API.
    """
    
    @abstractmethod
    def search():
        """
        Run the search query through the search engine API.
        
        This method must be implemented by subclasses to perform the actual search operation.
        """




class BaseRestfulAPI(BaseAPI):
    """
    Abstract base class for RESTful API classes.

    This class provides basic methods for making GET and POST requests
    using the `requests` library. Subclasses should define the `base_url`
    attribute to specify the base URL for the API.
    """
    base_url: str

    def __init__(self):
        self.session = requests.Session()



    def get(self, endpoint: str = '', **kwargs):
        """
        Make a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the GET request to.
            **kwargs: Additional arguments to pass to the `requests.Session.get` method.

        Returns:
            response: The response object from the GET request.
        """
        url = f"{self.base_url}{endpoint}"
        #print(f'url: {url}')
        response = self.session.get(url, **kwargs)
        return response




    def post(self, endpoint: str = '', **kwargs):
        """
        Make a POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the POST request to.
            **kwargs: Additional arguments to pass to the `requests.Session.post` method.

        Returns:
            response: The response object from the POST request.
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, **kwargs)
        return response



class BaseSeleniumAPI(BaseAPI):
    """
    Abstract base class for Selenium API classes.
    """
    base_url: str
    
    def __init__(self):
        self.options = Options()
        
        #if headless:
         #   self.options.add_argument('--headless')

        self.options.add_argument('--disable-gpu')
        self.options.add_argument("window-size=1200x600")
        self.options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
        self.driver = webdriver.Chrome(options = self.options)


    def scroll_to(self, path:str, type:str = 'xpath'):

        if type not in ['css', 'class', 'xpath']:
            raise ValueError("Invalid type specified. Type must be 'css', 'class', or 'xpath'.")

        if type == 'css':
            self.driver.execute_script("arguments[0].scrollIntoView();",
                                       self.driver.find_element(By.CSS_SELECTOR, path))
        elif type == 'class':
            self.driver.execute_script("arguments[0].scrollIntoView();",
                                       self.driver.find_element(By.CLASS_NAME, path))
        elif type == 'xpath':
            self.driver.execute_script("arguments[0].scrollIntoView();",
                                       self.driver.find_element(By.XPATH, path))


    def close(self):
        self.driver.quit()
