from aiohttp import web

from src.services.proxy import ProxyService


proxy = web.RouteTableDef()


@proxy.get('/proxy/manifest/{id}/{format_id}.mpd')
async def manifest_route(request: web.Request, *args, **kwargs) -> web.Response:
  return await ProxyService.manifest(request)


@proxy.get('/proxy/{kind}/{id}/{format_id}')
async def stream_media_route(request: web.Request, *args, **kwargs) -> web.StreamResponse:
  return await ProxyService.stream_media(request)


@proxy.route('*', '/auth/{path:.*}')
async def proxy_auth_route(request: web.Request, *args, **kwargs) -> web.Response:
  return await ProxyService.proxy_auth(request)
