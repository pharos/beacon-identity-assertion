# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from models.identity_assertion_response import IdentityAssertionResponse
from starlette.requests import Request

class BaseIdentityAssertionApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseIdentityAssertionApi.subclasses = BaseIdentityAssertionApi.subclasses + (cls,)
    async def assert_post(
        self,
        request: Request,
        assertion_type: str,
        assertion_value: str,
    ) -> IdentityAssertionResponse:
        """Given a identity assertion, this endpoint returns the identity claims"""
        ...