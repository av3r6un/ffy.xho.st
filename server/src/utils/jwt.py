import jwt

def verify_access_token(token: str) -> dict:
  from src import settings
  jwk_endpoint = f'https://{settings.AUTH_SERVER}/.well-known/jwks.json'
  jwk_client = jwt.PyJWKClient(jwk_endpoint)
  signing_key = jwk_client.get_signing_key_from_jwt(token).key
  return jwt.decode(
    token,
    signing_key,
    algorithms=['RS256'],
    issuer=settings.AUTH_SERVER,
    options={'require': ['exp', 'iat', 'iss', 'sub']}
  )
