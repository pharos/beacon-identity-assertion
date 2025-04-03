import logging
from data import assertion_data

from apis.base_identity_assertion_api import BaseIdentityAssertionApi
from models.identity_assertion_response import IdentityAssertionResponse
from models.error_response import ErrorResponse
from exceptions.http_error_response_exception import HTTPErrorResponseException
from fastapi import  HTTPException, status

logger = logging.getLogger("uvicorn.error")

class IdentityAssertionApi(BaseIdentityAssertionApi):
    async def assert_post(self, assertion_type: str, assertion_value: str):
        try:
            result = [item for item in assertion_data if item["assertion_key"] == assertion_type and item["assertion_value"] == assertion_value]
            if not result:
                logger.warning(f"No identity found with assertion_type={assertion_type} and assertion_value={assertion_value}")
                raise HTTPErrorResponseException(error_response=ErrorResponse( error = "card_not_found", error_description = "Failed to locate the request card with the database." ))

            return IdentityAssertionResponse.from_dict(result[0])
        except (HTTPException, HTTPErrorResponseException):
            raise
        except Exception as exception:
            logger.error(exception)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
