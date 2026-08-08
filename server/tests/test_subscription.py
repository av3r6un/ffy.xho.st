import unittest

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.models import PushSubscription, User
from src.models.base import Base
from src.services.subscription import PushSubscriptionService


class PushSubscriptionServiceTests(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    self.engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with self.engine.begin() as connection:
      await connection.run_sync(Base.metadata.create_all)
    self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

  async def asyncTearDown(self):
    await self.engine.dispose()

  async def test_creates_and_updates_subscription_without_duplicate(self):
    async with self.session_factory() as session:
      session.add(User('user01'))
      await session.flush()

      created = await PushSubscriptionService.upsert(
        session,
        'user01',
        'https://push.example.test/device',
        'first-p256dh',
        'first-auth',
        'First agent',
      )
      original_id = created.id

      updated = await PushSubscriptionService.upsert(
        session,
        'user01',
        'https://push.example.test/device',
        'second-p256dh',
        'second-auth',
        'Second agent',
      )

      self.assertEqual(updated.id, original_id)
      self.assertEqual(updated.p256dh, 'second-p256dh')
      self.assertEqual(updated.auth, 'second-auth')
      self.assertEqual(
        await PushSubscriptionService.get_active(
          session,
          'user01',
          updated.endpoint,
        ),
        updated,
      )
      self.assertEqual(
        len(await PushSubscription.all(session)),
        1,
      )

  async def test_revokes_and_restores_subscription(self):
    async with self.session_factory() as session:
      session.add(User('user01'))
      await session.flush()
      subscription = await PushSubscriptionService.upsert(
        session,
        'user01',
        'https://push.example.test/device',
        'p256dh',
        'auth',
      )

      self.assertTrue(await PushSubscriptionService.revoke(
        session,
        'user01',
        subscription.endpoint,
      ))
      self.assertIsNotNone(subscription.revoked_at)
      self.assertIsNone(await PushSubscriptionService.get_active(
        session,
        'user01',
        subscription.endpoint,
      ))

      restored = await PushSubscriptionService.upsert(
        session,
        'user01',
        subscription.endpoint,
        'new-p256dh',
        'new-auth',
      )
      self.assertIsNone(restored.revoked_at)

  async def test_does_not_revoke_another_users_subscription(self):
    async with self.session_factory() as session:
      session.add_all([User('user01'), User('user02')])
      await session.flush()
      subscription = await PushSubscriptionService.upsert(
        session,
        'user01',
        'https://push.example.test/device',
        'p256dh',
        'auth',
      )

      revoked = await PushSubscriptionService.revoke(
        session,
        'user02',
        subscription.endpoint,
      )

      self.assertFalse(revoked)
      self.assertIsNone(subscription.revoked_at)


if __name__ == '__main__':
  unittest.main()
