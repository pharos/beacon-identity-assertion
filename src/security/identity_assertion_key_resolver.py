from singleton import Singleton;
from http_message_signatures import HTTPSignatureKeyResolver

from jwt import PyJWKClient

class IdentityAssertionKeyResolver(HTTPSignatureKeyResolver, metaclass=Singleton):

    def __init__(self, url: str):
        self.jwks_client = PyJWKClient(url)

    def resolve_public_key(self, key_id: str):
        jwk = self.jwks_client.get_signing_key(key_id)
        if jwk is None:
            return None
        return jwk.key
