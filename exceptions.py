class CaptchaException(Exception):
    """Exception raised for CAPTCHA encounters."""
    def __init__(self, message="CAPTCHA encountered."):
        self.message = message
        super().__init__(self.message)

    

class NoResultsException(Exception):
    """Exception raised for no results found for the given search criteria."""
    def __init__(self, message="No results found for the given search criteria"):
        self.message = message
        super().__init__(self.message)

        

class NoAPIKeyException(Exception):
    """Exception raised when no API key is provided."""
    def __init__(self, message="No API key provided."):
        self.message = message
        super().__init__(self.message)