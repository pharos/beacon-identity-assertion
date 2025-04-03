# coding: utf-8

"""
    Identity Assertion

    Defines the Identity Assertion endpoints exposed by a server.

    The version of the OpenAPI document: 1.0.0
    Contact: contact@pharos.com
"""  # noqa: E501

import logging
import os
from data import assertion_data

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from apis.identity_assertion_api import router as IdentityAssertionApiRouter
from middleware.http_signature_middleware import HTTPSignatureMiddleware
from security.identity_assertion_key_resolver import IdentityAssertionKeyResolver
from exceptions.http_error_response_exception import HTTPErrorResponseException
from http_message_signatures import algorithms

app = FastAPI(
    title="Identity Assertion",
    description="Defines the Identity Assertion endpoint exposed by a server.",
    version="1.0.0",
)

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not any(endpoint in record.getMessage() for endpoint in ["/metrics", "/.diagnostics"])

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

@app.get("/.diagnostics/health-live")
@app.get("/.diagnostics/health-ready")
def health():
    return {"status": "ok"}

@app.exception_handler(HTTPErrorResponseException)
async def unicorn_exception_handler(request: Request, exception: HTTPErrorResponseException):
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.error.to_dict(),
    )

if "JWK_URL" not in os.environ:
    raise EnvironmentError(f"Environment variable 'JWK_URL' is not configured")
JWK_URL = os.getenv("JWK_URL", None)

app.add_middleware(HTTPSignatureMiddleware,
                   signature_algorithm=algorithms.RSA_PSS_SHA512,
                   key_resolver=IdentityAssertionKeyResolver(url=JWK_URL),
                   exclude_patterns=["^/metrics(?:[/\\?].*)?$", "^/.diagnostics(?:[/\\?].*)?$"])
app.include_router(IdentityAssertionApiRouter)

Instrumentator(
    excluded_handlers=["^/metrics(?:[/\\?].*)?$", "^/.diagnostics(?:[/\\?].*)?$"]
).instrument(app).expose(app)
