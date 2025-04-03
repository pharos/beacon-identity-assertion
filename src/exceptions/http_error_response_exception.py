
from models.error_response import ErrorResponse
from fastapi import status

class HTTPErrorResponseException(Exception):
    def __init__(self, error_response: ErrorResponse, status_code: status = status.HTTP_400_BAD_REQUEST ):
        self.error = error_response
        self.status_code = status_code
