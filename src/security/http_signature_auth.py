import datetime
from typing import Optional, Type

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import HTTPBase as HTTPBaseModel
from fastapi.security.base import SecurityBase

import requests
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from http_message_signatures import HTTPMessageVerifier, HTTPSignatureAlgorithm, HTTPSignatureKeyResolver
from http_message_signatures.exceptions import InvalidSignature

import logging
logger = logging.getLogger("uvicorn.error")

class HTTPSignatureAuth(SecurityBase):

    def __init__(
        self,
        *,
        scheme: str,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        signature_algorithm: Type[HTTPSignatureAlgorithm],
        key_resolver: HTTPSignatureKeyResolver,
        max_age: datetime.timedelta = datetime.timedelta(seconds=15)):
            self.model = HTTPBaseModel(scheme=scheme, description=description)
            self.scheme_name = scheme_name or self.__class__.__name__
            self.max_age = max_age
            self.verifier = HTTPMessageVerifier(signature_algorithm=signature_algorithm, key_resolver=key_resolver)

    async def __call__( self, request: Request ):
        self.verify(request)

    async def verify(self, request: Request):
        try:
            prepared_request = requests.Request(
                method=request.method,
                url=f'{request.url.scheme}://{request.url.hostname}{request.url.path}',
                headers={key: value for key, value in request.headers.items()},
            ).prepare()
            return self.verifier.verify(prepared_request, max_age=self.max_age)
        except InvalidSignature as invalid_signature:
            logger.error(invalid_signature)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        except Exception as exception:
            logger.error(exception)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
