# coding: utf-8

import importlib
import pkgutil

from apis.base_identity_assertion_api import BaseIdentityAssertionApi
import impl
from starlette.requests import Request

from fastapi import (  # noqa: F401
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Path,
    status,
)

from models.identity_assertion_response import IdentityAssertionResponse

router = APIRouter()

ns_pkg = impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)

@router.post(
    "/identity/assert",
    responses={
        400: {"description": "Invalid Request"},
        401: {"description": "Invalid Signature"},
        200: {"model": IdentityAssertionResponse, "description": "Claims about the identity asserted"},
    },
    tags=["default"],
    summary="Get identity claims based on the assertion",
    operation_id="IdentityAssertionRequests",
    response_model_by_alias=True,
)
async def assert_post(
    request: Request,
    assertion_type: str = Form(None, alias="assertion-type", description="The type of assertion being verified"),
    assertion_value: str = Form(None, alias="assertion-value", description="The value of assertion to be verified"),
) -> IdentityAssertionResponse:
    """Given a identity assertion, this endpoint returns the identity claims"""
    if not BaseIdentityAssertionApi.subclasses:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not implemented")
    response = await BaseIdentityAssertionApi.subclasses[0]().assert_post(assertion_type, assertion_value)
    if not response or response == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return response
