import unittest

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.models import ShortcutKey, User
from src.models.base import Base
from src.services.shortcut import ShortcutService


class ShortcutServiceTests(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    self.engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with self.engine.begin() as connection:
      await connection.run_sync(Base.metadata.create_all)
    self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

  async def asyncTearDown(self):
    await self.engine.dispose()

  async def test_issues_and_authenticates_token_without_storing_raw_secret(self):
    async with self.session_factory() as session:
      session.add(User('user01'))
      await session.flush()

      shortcut_key, token = await ShortcutService.issue(session, 'user01')
      self.assertTrue(token.startswith('mvs_'))
      self.assertNotEqual(shortcut_key.secret_hash, token)
      self.assertEqual(
        await ShortcutService.authenticate(session, token),
        shortcut_key,
      )

  async def test_issuing_new_token_keeps_existing_device_active(self):
    async with self.session_factory() as session:
      session.add(User('user01'))
      await session.flush()

      old_key, old_token = await ShortcutService.issue(session, 'user01')
      new_key, new_token = await ShortcutService.issue(session, 'user01')

      self.assertIsNone(old_key.revoked_at)
      self.assertEqual(await ShortcutService.authenticate(session, old_token), old_key)
      self.assertEqual(await ShortcutService.authenticate(session, new_token), new_key)

  async def test_rejects_malformed_and_revoked_tokens(self):
    async with self.session_factory() as session:
      session.add(User('user01'))
      await session.flush()
      shortcut_key, token = await ShortcutService.issue(session, 'user01')

      self.assertIsNone(await ShortcutService.authenticate(session, 'wrong'))
      self.assertTrue(await ShortcutService.revoke(session, 'user01', shortcut_key.id))
      self.assertIsNone(await ShortcutService.authenticate(session, token))


if __name__ == '__main__':
  unittest.main()
