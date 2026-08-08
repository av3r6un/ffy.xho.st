from pathlib import Path
import os

from aiohttp import web
from aiohttp.web import Request, RouteTableDef
main = RouteTableDef()


@main.get('/api/v/{id}')
async def watch(req: Request, session, *args, **kwargs):
  from src import youtube
  id = req.match_info.get('id') or req.query.get('v')
  if not id:
    raise ValueError('ID not specified.')
  info = youtube.find(id)
  return dict(**info.json, formats=info.formats.json)


@main.get('/health')
async def health(_: Request, *args, **kwargs):
  return {'service': 'mediavault', 'status': 'ok'}


@main.get('/{path:.*}')
async def static_app(req: Request, *args, **kwargs):
  first_segment = req.match_info.get('path', '').partition('/')[0]
  if first_segment in {'api', 'auth', 'proxy', 'health', 'shortcut'}:
    raise web.HTTPNotFound(text='Route not found')

  static_root = Path(
    os.getenv(
      'MEDIAVAULT_STATIC_DIR',
      Path(__file__).resolve().parents[2] / 'static',
    ),
  ).resolve()
  requested = (static_root / req.match_info.get('path', '')).resolve()

  if requested.is_relative_to(static_root) and requested.is_file():
    return web.FileResponse(requested)

  index = static_root / 'index.html'
  if index.is_file():
    return web.FileResponse(index)
  raise web.HTTPNotFound(text='Web application is not built')

  
