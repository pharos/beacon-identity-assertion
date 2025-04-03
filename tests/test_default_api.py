# coding: utf-8

from fastapi.testclient import TestClient


from models.identity_assertion_response import IdentityAssertionResponse  # noqa: F401


def test_assert_post(client: TestClient):
    """Test case for assert_post

    Get identity claims based on the assertion
    """

    headers = {
    }
    data = {
        "assertion_type": 'assertion_type_example',
        "assertion_value": 'assertion_value_example'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/assert".format(),
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

