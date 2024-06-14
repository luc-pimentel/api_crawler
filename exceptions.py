class CaptchaException(Exception):
    """Exception raised for CAPTCHA encounters."""
    def __init__(self, message="CAPTCHA encountered."):
        self.message = message
        super().__init__(self.message)



