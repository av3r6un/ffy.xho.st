import os
from datetime import datetime as dt

from aiohttp import web
from aiohttp.web import Request, RouteTableDef

from src.services import PushDeliveryStatus, PushService, PushSubscriptionService


subscriptions = RouteTableDef()


def _debug_enabled() -> bool:
  return os.getenv('DEBUG', '').strip().lower() in {'1', 'true', 'yes', 'on'}


def _required_string(value, name: str, max_length: int) -> str:
  if not isinstance(value, str) or not value.strip():
    raise web.HTTPBadRequest(text=f'{name} is required')
  value = value.strip()
  if len(value) > max_length:
    raise web.HTTPBadRequest(text=f'{name} is too long')
  return value


@subscriptions.get('/api/push/vapid-public-key')
async def get_vapid_public_key(req: Request, *args, **kwargs):
  return {'public_key': os.getenv('VAPID_PUBLIC_KEY')}


@subscriptions.get('/api/push/config')
async def get_push_config(_: Request, *args, **kwargs):
  return {'debug': _debug_enabled()}


@subscriptions.post('/api/push/subscriptions')
async def save_subscription(req: Request, session, *args, **kwargs):
  data = await req.json()
  keys = data.get('keys') if isinstance(data, dict) else None
  if not isinstance(keys, dict):
    raise web.HTTPBadRequest(text='keys are required')

  subscription = await PushSubscriptionService.upsert(
    session=session,
    user_uid=req['current_user'].uid,
    endpoint=_required_string(data.get('endpoint'), 'endpoint', 512),
    p256dh=_required_string(keys.get('p256dh'), 'p256dh', 255),
    auth=_required_string(keys.get('auth'), 'auth', 255),
    user_agent=req.headers.get('User-Agent', '')[:255] or None,
  )
  return subscription.json


@subscriptions.delete('/api/push/subscriptions')
async def revoke_subscription(req: Request, session, *args, **kwargs):
  data = await req.json()
  endpoint = _required_string(data.get('endpoint'), 'endpoint', 512)
  revoked = await PushSubscriptionService.revoke(
    session,
    req['current_user'].uid,
    endpoint,
  )
  return {'revoked': revoked}


@subscriptions.post('/api/push/test')
async def send_test_notification(req: Request, session, *args, **kwargs):
  data = await req.json()
  endpoint = _required_string(data.get('endpoint'), 'endpoint', 512)
  user = req['current_user']
  subscription = await PushSubscriptionService.get_active(
    session,
    user.uid,
    endpoint,
  )
  if subscription is None:
    raise web.HTTPNotFound(text='Push subscription not found')

  is_russian = user.language == 'ru'
  result = await PushService.send(
    subscription,
    {
      'title': 'Уведомления подключены' if is_russian else 'Notifications enabled',
      'body': (
        'MediaVault сможет сообщить, когда видео будет готово.'
        if is_russian
        else 'MediaVault can now notify you when a video is ready.'
      ),
      'url': '/',
      'tag': 'push-test',
      'lang': user.language,
    },
  )
  if result.status == PushDeliveryStatus.INVALID_SUBSCRIPTION:
    subscription.revoked_at = dt.now()

  return {
    'delivery_status': result.status,
    'status_code': result.status_code,
  }
