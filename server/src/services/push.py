import asyncio
import json
import logging
import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from pywebpush import WebPushException, webpush


class PushDeliveryStatus(StrEnum):
  SENT = 'sent'
  INVALID_SUBSCRIPTION = 'invalid_subscription'
  RETRYABLE = 'retryable'
  FAILED = 'failed'


@dataclass(frozen=True)
class PushDeliveryResult:
  status: PushDeliveryStatus
  status_code: int | None = None


class PushService:
  DEFAULT_TTL = 60 * 60

  @staticmethod
  def _subscription_info(subscription) -> dict:
    if isinstance(subscription, Mapping):
      endpoint = subscription['endpoint']
      p256dh = subscription['p256dh']
      auth = subscription['auth']
    else:
      endpoint = subscription.endpoint
      p256dh = subscription.p256dh
      auth = subscription.auth

    return {
      'endpoint': endpoint,
      'keys': {
        'p256dh': p256dh,
        'auth': auth,
      },
    }

  @classmethod
  async def send(
    cls,
    subscription,
    payload: Mapping,
    ttl: int = DEFAULT_TTL,
  ) -> PushDeliveryResult:
    try:
      await asyncio.to_thread(
        webpush,
        subscription_info=cls._subscription_info(subscription),
        data=json.dumps(payload, ensure_ascii=False, separators=(',', ':')),
        vapid_private_key=os.getenv('VAPID_PRIVATE_KEY'),
        vapid_claims={'sub': os.getenv('VAPID_SUBJECT')},
        ttl=ttl,
      )
      return PushDeliveryResult(PushDeliveryStatus.SENT)
    except WebPushException as exc:
      status_code = getattr(exc.response, 'status_code', None)

      if status_code in (404, 410):
        logging.info('Push subscription is no longer valid (HTTP %s)', status_code)
        status = PushDeliveryStatus.INVALID_SUBSCRIPTION
      elif status_code == 429 or (status_code is not None and status_code >= 500):
        logging.warning('Push delivery should be retried (HTTP %s)', status_code)
        status = PushDeliveryStatus.RETRYABLE
      else:
        logging.warning('Push delivery failed (HTTP %s)', status_code)
        status = PushDeliveryStatus.FAILED

      return PushDeliveryResult(status, status_code)
