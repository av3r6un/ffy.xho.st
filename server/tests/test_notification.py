import unittest
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.models import PushSubscription, User
from src.models.base import Base, Status
from src.services.notification import NotificationService
from src.services.push import PushDeliveryResult, PushDeliveryStatus


class NotificationServiceTests(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    self.engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with self.engine.begin() as connection:
      await connection.run_sync(Base.metadata.create_all)
    self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

  async def asyncTearDown(self):
    await self.engine.dispose()

  async def _seed(self, language='en'):
    session = self.session_factory()
    user = User('user01')
    user.language = language
    session.add(user)
    session.add(PushSubscription(
      'user01',
      'https://push.example.test/device',
      'p256dh',
      'auth',
    ))
    await session.commit()
    return session

  @patch('src.services.notification.PushService.send', new_callable=AsyncMock)
  async def test_sends_localized_ready_notification(self, send):
    send.return_value = PushDeliveryResult(PushDeliveryStatus.SENT)
    session = await self._seed('ru')
    async with session:
      await NotificationService.notify_session(
        session,
        'user01',
        'session1',
        Status.READY,
        'Название видео',
      )

    payload = send.await_args.args[1]
    self.assertEqual(payload['title'], 'Видео готово')
    self.assertEqual(payload['body'], 'Название видео')
    self.assertEqual(payload['url'], '/#/watch?session=session1')

  @patch('src.services.notification.asyncio.sleep', new_callable=AsyncMock)
  @patch('src.services.notification.PushService.send', new_callable=AsyncMock)
  async def test_retries_temporary_failure(self, send, sleep):
    send.side_effect = [
      PushDeliveryResult(PushDeliveryStatus.RETRYABLE, 503),
      PushDeliveryResult(PushDeliveryStatus.SENT),
    ]
    session = await self._seed()
    async with session:
      await NotificationService.notify_session(
        session,
        'user01',
        'session1',
        Status.FAILED,
      )

    self.assertEqual(send.await_count, 2)
    sleep.assert_awaited_once_with(1)

  @patch('src.services.notification.PushService.send', new_callable=AsyncMock)
  async def test_revokes_expired_subscription(self, send):
    send.return_value = PushDeliveryResult(
      PushDeliveryStatus.INVALID_SUBSCRIPTION,
      410,
    )
    session = await self._seed()
    async with session:
      await NotificationService.notify_session(
        session,
        'user01',
        'session1',
        Status.READY,
      )
      subscription = await PushSubscription.first(session, user_uid='user01')
      self.assertIsNotNone(subscription.revoked_at)


if __name__ == '__main__':
  unittest.main()
