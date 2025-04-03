
import datetime
import re
from typing import Type, List

from http_message_signatures import HTTPSignatureAlgorithm, HTTPSignatureKeyResolver

from security.http_signature_auth import HTTPSignatureAuth
from security.http_content_digest_auth import HTTPContentDigestAuth

from starlette.middleware.base import BaseHTTPMiddleware

import logging
logger = logging.getLogger("uvicorn.error")

class HTTPSignatureMiddleware(BaseHTTPMiddleware):

    def __init__(self, app,
        signature_algorithm: Type[HTTPSignatureAlgorithm],
        key_resolver: HTTPSignatureKeyResolver,
        max_age: datetime.timedelta = datetime.timedelta(seconds=15),
        exclude_patterns: List[str] = None):
        super().__init__(app)

        self.signature_auth = HTTPSignatureAuth(scheme="http-signature",signature_algorithm=signature_algorithm, key_resolver=key_resolver, max_age=max_age)
        self.content_digest_auth = HTTPContentDigestAuth(scheme="http-content-digest")

        # Try to compile patterns
        self.exclude_paths = []
        if exclude_patterns and isinstance(exclude_patterns, list):
            for path in exclude_patterns:
                try:
                    self.exclude_paths.append(re.compile(path))
                except re.error:
                    logger.error("Could not compile regex for exclude pattern %s", path)

    async def _exclude_path(self, path: str) -> bool:
        """
        Checks if a path should be excluded from authentication

        :param path: The path to check
        :type path: str
        :return: True if the path should be excluded, False otherwise
        """
        for pattern in self.exclude_paths:
            if pattern.match(path):
                return True
        return False

    async def dispatch(self, request, call_next):
        # Extract path from scope
        if await self._exclude_path(request.url.path):
            logger.debug("Skipping authentication for excluded path %s", request.url.path)
            response = await call_next(request)
            return response

        await self.content_digest_auth.verify(request)
        verifyResult = await self.signature_auth.verify(request)

        #  SECURITY CONSIDERATION:
        #  If verifyResult contains a 'nonce' key, then we MUST
        #    * verify it has not been used before
        #    * store it for future reference

        # Proceed with the request
        response = await call_next(request)
        return response