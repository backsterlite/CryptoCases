

class AppException(Exception):
    """Base app exception with custom message"""
    def __init__(self, message: str = "Unhandled exception", status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message, self.status_code)