from .base import AppException

class BalanceTooLow(AppException):
    def __init__(self):
        super().__init__(message="Insufficient balance for this operation.", status_code=400)