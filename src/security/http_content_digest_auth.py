import base64
import hashlib
from typing import Optional, Type

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import HTTPBase as HTTPBaseModel
from fastapi.security.base import SecurityBase

from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from http_message_signatures.exceptions import InvalidSignature

import logging
logger = logging.getLogger("uvicorn.error")

class HTTPContentDigestAuth(SecurityBase):

    def __init__(
        self,
        *,
        scheme: str,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None):
            self.model = HTTPBaseModel(scheme=scheme, description=description)
            self.scheme_name = scheme_name or self.__class__.__name__

    async def __call__( self, request: Request ):
        self.verify(request)

    async def verify(self, request: Request):
        try:
            # Content-Digest header is optional, e.g. Content-Digest: SHA-256=Ou1uWZ4BkQynu6Oir+u4XliIJpV06220rHRocK6VNY0=
            content_digest = request.headers.get("content-digest")
            if content_digest is None:
                logging.warning("No content-digest header found")
                return # No content-digest header, nothing to verify

            # Extract the algorithm and the digest from the header
            algorithm, digest = content_digest.split("=", 1)
            match algorithm.lower():
                case "sha-256":
                    hash_func = hashlib.sha256
                case "sha-512":
                    hash_func = hashlib.sha512
                case _:
                    logging.error(f"Unsupported digest algorithm: {algorithm}, only 'sha-256' and 'sha-512' are supported")
                    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=f"Unsupported digest algorithm: {algorithm}, only 'sha-256' and 'sha-512' are supported")
            digest = digest.strip(':')

            body = await request.body()
            # Compute the digest of the request body
            computed_digest = base64.b64encode(hash_func(body).digest()).decode()

            # Compare the computed digest with the digest from the header
            if computed_digest != digest:
                logging.error(f"Invalid content digest: {digest} != {computed_digest}")
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid content digest")
        except HTTPException:
            raise
        except Exception as exception:
            logger.error(exception)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
