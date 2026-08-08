import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pywebpush import WebPushException

from src.services.push import PushDeliveryStatus, PushService


class PushServiceTests(unittest.IsolatedAsyncioTestCase):
  def setUp(self):
    self.previous_env = {
      name: os.environ.get(name)
      for name in ('VAPID_PRIVATE_KEY', 'VAPID_SUBJECT')
    }
    os.environ['VAPID_PRIVATE_KEY'] = 'private-key'
    os.environ['VAPID_SUBJECT'] = 'mailto:admin@voidspace.ru'
    self.subscription = {
      'endpoint': 'https://push.example.test/subscription',
      'p256dh': 'client-public-key',
      'auth': 'client-auth-secret',
    }

  def tearDown(self):
    for name, value in self.previous_env.items():
      if value is None:
        os.environ.pop(name, None)
      else:
        os.environ[name] = value

  @patch('src.services.push.webpush')
  async def test_sends_json_payload(self, mocked_webpush):
    result = await PushService.send(
      self.subscription,
      {'title': 'Готово', 'url': '/#/watch?session=abc123'},
      ttl=120,
    )

    self.assertEqual(result.status, PushDeliveryStatus.SENT)
    kwargs = mocked_webpush.call_args.kwargs
    self.assertEqual(
      kwargs['subscription_info'],
      {
        'endpoint': self.subscription['endpoint'],
        'keys': {
          'p256dh': self.subscription['p256dh'],
          'auth': self.subscription['auth'],
        },
      },
    )
    self.assertEqual(json.loads(kwargs['data'])['title'], 'Готово')
    self.assertEqual(kwargs['vapid_private_key'], 'private-key')
    self.assertEqual(
      kwargs['vapid_claims'],
      {'sub': 'mailto:admin@voidspace.ru'},
    )
    self.assertEqual(kwargs['ttl'], 120)

  async def test_marks_gone_subscription_as_invalid(self):
    result = await self._send_with_http_error(410)

    self.assertEqual(result.status, PushDeliveryStatus.INVALID_SUBSCRIPTION)
    self.assertEqual(result.status_code, 410)

  async def test_marks_rate_limit_as_retryable(self):
    result = await self._send_with_http_error(429)

    self.assertEqual(result.status, PushDeliveryStatus.RETRYABLE)

  async def test_marks_server_error_as_retryable(self):
    result = await self._send_with_http_error(503)

    self.assertEqual(result.status, PushDeliveryStatus.RETRYABLE)

  async def test_marks_other_errors_as_failed(self):
    result = await self._send_with_http_error(400)

    self.assertEqual(result.status, PushDeliveryStatus.FAILED)

  async def _send_with_http_error(self, status_code):
    response = SimpleNamespace(status_code=status_code, text='response omitted')
    error = WebPushException('delivery failed', response=response)
    with patch('src.services.push.webpush', side_effect=error):
      return await PushService.send(self.subscription, {'title': 'Ready'})


if __name__ == '__main__':
  unittest.main()
