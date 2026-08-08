import hashlib
import secrets
from datetime import datetime as dt

from sqlalchemy import select

from src.models import ShortcutKey


class ShortcutService:
  TOKEN_PREFIX = 'mvs_'

  @staticmethod
  def _hash(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

  @classmethod
  async def issue(cls, session, user_uid: str, name: str = 'Apple Shortcut') -> tuple[ShortcutKey, str]:
    token = cls.TOKEN_PREFIX + secrets.token_urlsafe(32)
    shortcut_key = ShortcutKey(
      user_uid=user_uid,
      secret_hash=cls._hash(token),
      name=name,
    )
    session.add(shortcut_key)
    await session.flush()
    return shortcut_key, token

  @classmethod
  async def authenticate(cls, session, token: str | None) -> ShortcutKey | None:
    if not token or not token.startswith(cls.TOKEN_PREFIX):
      return None

    result = await session.execute(
      select(ShortcutKey).where(
        ShortcutKey.secret_hash == cls._hash(token),
        ShortcutKey.revoked_at.is_(None),
      ),
    )
    shortcut_key = result.scalar_one_or_none()
    if shortcut_key:
      shortcut_key.last_used_at = dt.now()
      await session.flush()
    return shortcut_key

  @classmethod
  async def revoke(cls, session, user_uid: str, key_id: int) -> bool:
    shortcut_key = await ShortcutKey.first(
      session,
      id=key_id,
      user_uid=user_uid,
      revoked_at__isnull=True,
    )
    if not shortcut_key:
      return False
    shortcut_key.revoked_at = dt.now()
    await session.flush()
    return True
