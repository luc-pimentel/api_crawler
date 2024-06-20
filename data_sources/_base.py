import requests
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from ..exceptions import NoAPIKeyException
import os
import warnings



class BaseAPI(ABC):
    """
    Abstract base class for other API classes.
    It enforces the implementation of the __init__ method in subclasses.
    """



    @staticmethod
    def _get_api_key(api_key: str, env_var: str, action: str = 'raise', message: str = None) -> str:
        """
        Util method to retrieve and validate the API key.

        This method attempts to retrieve the API key from the provided parameter.
        If the parameter is None, it tries to fetch the key from the environment variable.
        If the key is still None, it raises a NoAPIKeyException.

        Args:
            api_key (str): The API key provided as a parameter.
            env_var (str): The name of the environment variable to fetch the API key from.

        Returns:
            str: The validated API key.

        Raises:
            NoAPIKeyException: If the API key is not provided and not found in the environment variables.
        """
        if action not in ['raise', 'warn']:
            raise ValueError("Invalid action. Only 'raise' or 'warn' are allowed.")


        if api_key is None:
            api_key = os.environ.get(env_var)
        if api_key is None:
            if action == 'raise':
                raise NoAPIKeyException(message or f"{env_var} not provided. Please set the {env_var} environment variable or pass it to the object via the api_key parameter.")
            elif action == 'warn':
                warnings.warn(message or f"{env_var} not provided. Please set the {env_var} environment variable or pass it to the object via the api_key parameter.", category=NoAPIKeyException)
        return api_key






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
