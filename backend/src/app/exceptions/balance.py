from .base import AppException

class BalanceTooLow(AppException):
    def __init__(self, message: str | None):
        if message is None:
            self.message = message
        else:
            self.message = "Insufficient balance for this operation."
        super().__init__(message=self.message, status_code=400) # type: ignore