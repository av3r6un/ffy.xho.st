import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError


class PlaybackTokenService:
  ALGORITHM = 'HS256'
  AUDIENCE = 'mediavault-proxy'
  ISSUER = 'mediavault'
  TTL = timedelta(hours=24)

  @staticmethod
  def _secret() -> str:
    secret = os.getenv('PLAYBACK_SECRET') or os.getenv('SECRET_KEY')
    if not secret or len(secret) < 32:
      raise RuntimeError('PLAYBACK_SECRET must contain at least 32 characters.')
    return secret

  @classmethod
  def issue(cls, session_uid: str, video_id: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
      {
        'iss': cls.ISSUER,
        'aud': cls.AUDIENCE,
        'sub': session_uid,
        'vid': video_id,
        'iat': now,
        'exp': now + cls.TTL,
      },
      cls._secret(),
      algorithm=cls.ALGORITHM,
    )

  @classmethod
  def verify(cls, token: str, video_id: str) -> dict:
    payload = jwt.decode(
      token,
      cls._secret(),
      algorithms=[cls.ALGORITHM],
      audience=cls.AUDIENCE,
      issuer=cls.ISSUER,
      options={'require': ['exp', 'iat', 'iss', 'aud', 'sub', 'vid']},
    )
    if payload['vid'] != video_id:
      raise InvalidTokenError('Playback token belongs to another video.')
    return payload
