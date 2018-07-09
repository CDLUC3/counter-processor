class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ApiError(Error):
    """Exception raised when encountering errors accessing someone else's APIs

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
