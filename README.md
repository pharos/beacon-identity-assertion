
# Identity Assertion

The identity assertion is a mechanism to assert the identity of a user. It is used to verify the
identity of a user when they are trying to access a service.  The identity assertion is a process that
involves verifying the identity of a user by using a set of attributes.  The attributes can be a
username and password, an encrypted card value, or any other form of authentication.

### Identity Assertion Endpoint

The identity assertion endpoint returns information about the user identity based on the provided user
attributes.  The endpoint at a minimum needs to return the users email address or an error state.  Any
error returned by the endpoint should be in a standard format that includes a message and a status code.

### Identity Assertion Security

To prevent identity assertion attacks, the identity assertion endpoint MUST be protected.  The protection
requires the use of an HTTP Signature [RFC9241](https://datatracker.ietf.org/doc/rfc9421/) and the
content-digest header [RFC9530](https://datatracker.ietf.org/doc/rfc9530/).  The HTTP signature is
signed using a private key defined by the client and verified by the server using the public key.  The
"content-digest" header is used to verify the integrity of the request body using an SHA256 hash value.
The "content-digest" header is included as part of the HTTP signature.

### Identity Assertion Request

The identity assertion endpoint is called using an HTTP POST [RFC7231](https://datatracker.ietf.org/doc/html/rfc7231)
request with parameters sent as "application/x-www-form-urlencoded" data defined in [W3C.REC-html5-20141028](https://datatracker.ietf.org/doc/html/rfc7662#ref-W3C.REC-html5-20141028).

assertion-type

> **REQUIRED**.  The type of assertion being made.  The value of this parameter is a string that
  identifies the type of assertion being made.  The format of the _assertion-value_ is also determined
  by the assertion-type.

assertion-value

> **REQUIRED**. The value of the assertion being made.  The format of the _assertion-value_ is determined
  by the assertion-type.  The assertion-value is passed as a based64 [RFC4648](https://datatracker.ietf.org/doc/html/rfc4648)
  encoded string as the contents may be raw binary data from the originating assertion source.

For example, the following shows a request to the identity assertion endpoint, requesting a user to be
asserted based on a card value.  Example signed using test tool [HTTP Message Signatures](https://httpsig.org/)

```http
 POST /identity/assertion HTTP/1.1
 Host: server.example.com
 Accept: application/json
 Content-Type: application/x-www-form-urlencoded
 Content-Digest: SAH256=lXZiejHeZ9vdcZIKA+3XABBw3M+JIkIoXwzn9DcEtYg=
 Signature-Input: sig=();alg="rsa-pss-sha512";keyid="sig";created=1733426755
 Signature: sig=:K1xR00fyML4MKHAm9SLTx/MLfI+qDGUr7bIma0RdF8kiYS+ZmsJGwKMXBYZJXAQraL1xlEY6cMp6BioyPpxMzelQFs1IIegZi09tM3CN3Xr4pu1kiJXh1AgfSnQCaG/yfmjhuvgft0V999SS9vxpCDBrVBHYxaDJwGrNj9GaykpDn0XYzM84xlRCfuiuOJusRk3TDacqDW/MIG+GecBBiBiX8d36oNibv3mEmmJ29s/D+n5DxwQs+6WUXaMu27dEPRykydzX3loltlT+kER3dIEpnArtxxH8w/8rCMujS3IF530+ySKJc9VRnhL2zEEkVoUnK6/PxI6MOqRYxmHMog==:

 assertion-type=urn:identity:assertion:card&
 assertion-value=Q2FyZCB2YWx1ZQ==
```

### Identity Assertion Response

The identity assertion endpoint returns a JSON object [RFC7159](https://datatracker.ietf.org/doc/html/rfc7159) in
"application/json" format with the following members:

email

> **REQUIRED**. The email address of the user being asserted.

The following is a non-normative example response when the identity assertion is successful:

```http
 HTTP/1.1 200 OK
 Content-Type: application/json

 {
   "email": "wilie.e.coyote@amce.com",
 }
```

### Identity Assertion Error Response

If the identity assertion fails, the server SHOULD inform the client of the error.   Any 4XX or 5XX HTTP status code SHALL
be treated as a failed request and the response body SHOULD contain a JSON object [RFC7159](https://datatracker.ietf.org/doc/html/rfc7159)
describing the failure condition.

error

> **REQUIRED**. A string that states the error code, which MAY be one of the following
>   * **invalid_request**:  The request is missing a required parameter, includes an  invalid parameter value, includes a
>     parameter more than once, or is otherwise malformed.
>   * **access_denied**:  The server denied the request.
>   * *server_error**: The server encountered an unexpected condition that prevented it from fulfilling the request.
>   * **temporarily_unavailable**: The server is currently unable to handle the request.

error_description:

> **OPTIONAL**. A human-readable message providing additional information, used to assist the client developer in understanding
> the error that occurred.

The following is a non-normative example response when the identity assertion is unsuccessful:

```http
 HTTP/1.1 400 Bad Request
 Content-Type: application/json

 {
   "error": "invalid_request",
   "error_description": "The assertion type is not supported."
 }
```

```http
 HTTP/1.1 401 Unauthorized
 Content-Type: application/json

 {
   "error": "access_denied",
   "error_description": "The assertion value is invalid."
 }
```

## Requirements.

Python >= 3.7

## Installation & Usage

To run the server, please execute the following from the root directory:

```bash
pip3 install -r requirements.txt
CSV_DATA_FILE="data.csv" JWK_URL="https://<beacon-host-name>/common/.well-known/identity-assertions.jwks" PYTHONPATH=src uvicorn main:app --host 0.0.0.0 --port 8080
```

and open your browser at `http://localhost:8080/docs/` to see the docs.

## Tests

To run the tests:

```bash
pip3 install pytest
PYTHONPATH=src pytest tests
```