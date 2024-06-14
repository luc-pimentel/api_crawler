class CaptchaException(Exception):
    """Exception raised for CAPTCHA encounters."""
    def __init__(self, message="CAPTCHA encountered."):
        self.message = message
        super().__init__(self.message)



class NoResultsException(Exception):
    def __init__(self, message="No results found for the given search criteria"):
        self.message = message
        super().__init__(self.message)