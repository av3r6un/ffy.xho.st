from aiohttp.web import Request, RouteTableDef

from src.exceptions import JSRError
from src.models.base import Status
from src.services import NotificationService, SessionService, ShortcutService


shortcuts = RouteTableDef()


def _bearer_token(req: Request) -> str | None:
  scheme, _, token = req.headers.get('Authorization', '').partition(' ')
  if scheme.lower() != 'bearer' or not token:
    return None
  return token.strip()


@shortcuts.post('/api/shortcuts')
async def create_shortcut_key(req: Request, session, *args, **kwargs):
  data = await req.json()
  name = data.get('name', 'Apple Shortcut') if isinstance(data, dict) else 'Apple Shortcut'
  if not isinstance(name, str) or not name.strip():
    raise JSRError('invalid_payload', message='Shortcut name is required.')

  shortcut_key, token = await ShortcutService.issue(
    session,
    req['current_user'].uid,
    name.strip()[:50],
  )
  return {
    'id': shortcut_key.id,
    'name': shortcut_key.name,
    'token': token,
  }


@shortcuts.delete('/api/shortcuts/{id}')
async def revoke_shortcut_key(req: Request, session, *args, **kwargs):
  try:
    key_id = int(req.match_info['id'])
  except (TypeError, ValueError):
    raise JSRError('invalid_payload', message='Invalid shortcut key ID.')
  return {'revoked': await ShortcutService.revoke(
    session,
    req['current_user'].uid,
    key_id,
  )}


@shortcuts.post('/shortcut/sessions')
async def create_shortcut_session(req: Request, session, *args, **kwargs):
  shortcut_key = await ShortcutService.authenticate(session, _bearer_token(req))
  if not shortcut_key:
    raise JSRError('unauthorized', message='Invalid or revoked Shortcut token.')

  try:
    data = await req.json()
  except Exception:
    raise JSRError('invalid_payload', message='A JSON body is required.')

  from src import youtube

  video_url = data.get('video_url') if isinstance(data, dict) else None
  video_id = youtube.extract_id_from_url(video_url)
  payload = await SessionService.prepare(
    req.app,
    session,
    shortcut_key.user_uid,
    video_id,
  )

  if payload['status'] == Status.READY.value:
    await session.commit()
    await NotificationService.notify_session(
      session,
      shortcut_key.user_uid,
      payload['uid'],
      Status.READY,
    )

  return payload
