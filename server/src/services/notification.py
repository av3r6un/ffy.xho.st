import asyncio
import logging
from datetime import datetime as dt

from src.models import User
from src.models.base import Status

from .push import PushDeliveryStatus, PushService
from .subscription import PushSubscriptionService


class NotificationService:
  RETRY_DELAYS = (1, 5)

  @staticmethod
  def _payload(status: Status, session_uid: str, language: str, title=None):
    is_russian = language == 'ru'
    if status is Status.READY:
      return {
        'title': 'Видео готово' if is_russian else 'Video is ready',
        'body': title or (
          'Нажмите, чтобы начать просмотр.'
          if is_russian
          else 'Tap to start watching.'
        ),
        'url': f'/#/watch?session={session_uid}',
        'tag': f'session-{session_uid}',
        'lang': language,
      }

    return {
      'title': 'Не удалось подготовить видео' if is_russian else 'Video preparation failed',
      'body': (
        'Попробуйте отправить видео ещё раз.'
        if is_russian
        else 'Please try sending the video again.'
      ),
      'url': '/#/',
      'tag': f'session-{session_uid}',
      'lang': language,
    }

  @classmethod
  async def notify_session(
    cls,
    session,
    user_uid: str,
    session_uid: str,
    status: Status,
    title: str | None = None,
  ) -> None:
    user = await User.first(session, uid=user_uid)
    if user is None:
      logging.warning('Notification user %s was not found', user_uid)
      return

    subscriptions = await PushSubscriptionService.active_for_user(session, user_uid)
    if not subscriptions:
      logging.info('No active push subscriptions for user %s', user_uid)
      return

    payload = cls._payload(status, session_uid, user.language, title)
    results = await asyncio.gather(
      *(cls._deliver(subscription, payload) for subscription in subscriptions),
      return_exceptions=True,
    )
    for subscription, result in zip(subscriptions, results):
      if isinstance(result, Exception):
        logging.error(
          'Push delivery crashed for subscription %s',
          subscription.id,
          exc_info=(type(result), result, result.__traceback__),
        )
      elif result.status == PushDeliveryStatus.INVALID_SUBSCRIPTION:
        subscription.revoked_at = dt.now()

    await session.commit()

  @classmethod
  async def _deliver(cls, subscription, payload):
    result = await PushService.send(subscription, payload)
    for delay in cls.RETRY_DELAYS:
      if result.status != PushDeliveryStatus.RETRYABLE:
        break
      await asyncio.sleep(delay)
      result = await PushService.send(subscription, payload)
    return result
