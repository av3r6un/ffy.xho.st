from aiohttp.web import RouteTableDef, Request
from src.services import SessionService


sessions = RouteTableDef()


@sessions.post('/api/sessions')
async def create_session(req: Request, session, *args, **kwargs):
  from src import youtube
  data = await req.json()
  video_id = youtube.extract_id_from_url(data.get('video_url'))
  user = req['current_user']
  return await SessionService.prepare(req.app, session, user.uid, video_id)


@sessions.get('/api/sessions/{uid}')
async def get_session(req: Request, session, *args, **kwargs):
  user = req['current_user']
  return await SessionService.get_payload(
    session,
    req.match_info['uid'],
    user.uid,
  )
