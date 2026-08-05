import asyncio
import logging
import os
import re
import time
from collections.abc import Mapping
from urllib.parse import quote, urlencode
from xml.etree import ElementTree

from aiohttp import (
  ClientError,
  ClientSession,
  ClientTimeout,
  DummyCookieJar,
  web,
)
from jwt import InvalidTokenError
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from .playback import PlaybackTokenService

VIDEO_SESSION = web.AppKey('video_proxy_session', ClientSession)
AUDIO_SESSION = web.AppKey('audio_proxy_session', ClientSession)
AUTH_SESSION = web.AppKey('auth_proxy_session', ClientSession)
MEDIA_CACHE = web.AppKey('proxy_media_cache', dict)

VIDEO_ID_RE = re.compile(r'^[A-Za-z0-9_-]{11}$')
FORMAT_ID_RE = re.compile(r'^[A-Za-z0-9._-]{1,64}$')

FORWARDED_REQUEST_HEADERS = ('Range', 'If-Range')
FORWARDED_RESPONSE_HEADERS = (
  'Accept-Ranges',
  'Cache-Control',
  'Content-Length',
  'Content-Range',
  'Content-Type',
  'ETag',
  'Expires',
  'Last-Modified',
)

DASH_NAMESPACE = 'urn:mpeg:dash:schema:mpd:2011'
MP4_PROBE_CHUNK_SIZE = 256 * 1024
MP4_PROBE_MAX_SIZE = 8 * 1024 * 1024
ElementTree.register_namespace('', DASH_NAMESPACE)


def _dash_tag(name: str) -> str:
  return f'{{{DASH_NAMESPACE}}}{name}'


def _iso_duration(seconds: int | float) -> str:
  value = f'{max(0, float(seconds)):.3f}'.rstrip('0').rstrip('.')
  return f'PT{value or "0"}S'


def _add_representation(
  adaptation: ElementTree.Element,
  source: Mapping,
  base_url: str,
  initialization_range: tuple[int, int],
  index_range: tuple[int, int],
) -> None:
  attributes = {
    'id': str(source['id']),
    'bandwidth': str(source['bandwidth']),
    'mimeType': str(source['mimeType']),
    'codecs': str(source['codecs']),
  }
  optional_attributes = {
    'width': source.get('width'),
    'height': source.get('height'),
    'frameRate': source.get('frameRate'),
    'audioSamplingRate': source.get('audioSamplingRate'),
  }
  attributes.update({
    key: str(value)
    for key, value in optional_attributes.items()
    if value is not None
  })

  representation = ElementTree.SubElement(
    adaptation,
    _dash_tag('Representation'),
    attributes,
  )
  ElementTree.SubElement(representation, _dash_tag('BaseURL')).text = base_url
  segment_base = ElementTree.SubElement(
    representation,
    _dash_tag('SegmentBase'),
    {
      'indexRange': f'{index_range[0]}-{index_range[1]}',
      'indexRangeExact': 'true',
    },
  )
  ElementTree.SubElement(
    segment_base,
    _dash_tag('Initialization'),
    {'range': f'{initialization_range[0]}-{initialization_range[1]}'},
  )


def _build_manifest(
  video_id: str,
  media,
  audio_id: str,
  video_format_id: str,
  segment_ranges: Mapping[str, tuple[tuple[int, int], tuple[int, int]]],
  playback_token: str,
) -> bytes:
  video_format = media.formats[video_format_id]
  audio_format = media.formats[audio_id]
  if video_format is None or not video_format.vcodec or video_format.acodec:
    raise ValueError(f'Video format {video_format_id} is unavailable')
  if audio_format is None or not audio_format.acodec:
    raise ValueError(f'Audio format {audio_id} is unavailable')

  duration = _iso_duration(media.duration)
  playback_query = urlencode({'token': playback_token})
  mpd = ElementTree.Element(_dash_tag('MPD'), {
    'type': 'static',
    'profiles': 'urn:mpeg:dash:profile:isoff-on-demand:2011',
    'mediaPresentationDuration': duration,
    'minBufferTime': 'PT1.5S',
  })
  period = ElementTree.SubElement(mpd, _dash_tag('Period'), {
    'id': '0',
    'start': 'PT0S',
    'duration': duration,
  })

  video_adaptation = ElementTree.SubElement(period, _dash_tag('AdaptationSet'), {
    'id': 'video',
    'contentType': 'video',
    'segmentAlignment': 'true',
    'startWithSAP': '1',
  })
  _add_representation(
    video_adaptation,
    video_format.detailed,
    f'/proxy/video/{video_id}/{quote(video_format_id, safe="")}?{playback_query}',
    *segment_ranges[video_format_id],
  )

  audio_source = audio_format.detailed
  audio_adaptation = ElementTree.SubElement(period, _dash_tag('AdaptationSet'), {
    'id': 'audio',
    'contentType': 'audio',
    'segmentAlignment': 'true',
    'startWithSAP': '1',
  })
  ElementTree.SubElement(audio_adaptation, _dash_tag('AudioChannelConfiguration'), {
    'schemeIdUri': 'urn:mpeg:dash:23003:3:audio_channel_configuration:2011',
    'value': str(audio_source.get('audioChannels') or 2),
  })
  _add_representation(
    audio_adaptation,
    audio_source,
    f'/proxy/audio/{video_id}/{quote(audio_id, safe="")}?{playback_query}',
    *segment_ranges[audio_id],
  )

  return ElementTree.tostring(mpd, encoding='utf-8', xml_declaration=True)


def _require_playback_token(request: web.Request, video_id: str) -> str:
  token = request.query.get('token')
  if not token:
    raise web.HTTPUnauthorized(text='Playback token is required')
  try:
    PlaybackTokenService.verify(token, video_id)
  except InvalidTokenError as ex:
    raise web.HTTPUnauthorized(text='Playback token is invalid') from ex
  return token


def _manifest_response(request: web.Request, body: bytes) -> web.Response:
  headers = {
    'Accept-Ranges': 'bytes',
    'Cache-Control': 'private, max-age=60',
  }
  if 'Range' not in request.headers:
    return web.Response(
      body=body,
      content_type='application/dash+xml',
      charset='utf-8',
      headers=headers,
    )

  total = len(body)
  try:
    requested = request.http_range
  except ValueError as ex:
    raise web.HTTPRequestRangeNotSatisfiable(
      headers={'Content-Range': f'bytes */{total}'},
    ) from ex

  start = requested.start or 0
  if start < 0:
    start = max(total + start, 0)
  if start >= total:
    raise web.HTTPRequestRangeNotSatisfiable(
      headers={'Content-Range': f'bytes */{total}'},
    )

  end = min(requested.stop or total, total)
  partial = body[start:end]
  headers['Content-Range'] = f'bytes {start}-{end - 1}/{total}'
  return web.Response(
    body=partial,
    status=web.HTTPPartialContent.status_code,
    content_type='application/dash+xml',
    charset='utf-8',
    headers=headers,
  )


def _parse_segment_ranges(data: bytes) -> tuple[tuple[int, int], tuple[int, int]]:
  offset = 0
  while offset + 8 <= len(data):
    size = int.from_bytes(data[offset:offset + 4], 'big')
    box_type = data[offset + 4:offset + 8]
    header_size = 8

    if size == 1:
      if offset + 16 > len(data):
        break
      size = int.from_bytes(data[offset + 8:offset + 16], 'big')
      header_size = 16
    elif size == 0:
      size = len(data) - offset

    if size < header_size or offset + size > len(data):
      break
    if box_type == b'sidx':
      if offset == 0:
        raise ValueError('MP4 sidx box has no initialization section')
      return (0, offset - 1), (offset, offset + size - 1)

    offset += size

  raise ValueError('Unable to locate MP4 sidx box')


def _resolve_media(video_id: str, format_id: str, kind: str) -> tuple[str, dict[str, str]]:
  video_url = f'https://www.youtube.com/watch?v={video_id}'
  options = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'format': format_id,
  }

  with YoutubeDL(options) as ydl:
    info = ydl.extract_info(video_url, download=False)

  if not isinstance(info, Mapping):
    raise ValueError('yt-dlp returned invalid media information')

  media_url = info.get('url')
  if not isinstance(media_url, str) or not media_url:
    raise ValueError(f'Format {format_id} has no direct media URL')

  vcodec = info.get('vcodec')
  acodec = info.get('acodec')
  if kind == 'video' and vcodec in (None, 'none'):
    raise ValueError(f'Format {format_id} is not a video format')
  if kind == 'audio' and acodec in (None, 'none'):
    raise ValueError(f'Format {format_id} is not an audio format')

  headers = info.get('http_headers') or {}
  return media_url, {str(key): str(value) for key, value in headers.items()}


async def proxy_sessions(app: web.Application):
  timeout = ClientTimeout(total=None, connect=30, sock_connect=30, sock_read=None)
  session_options = {
    'auto_decompress': False,
    'cookie_jar': DummyCookieJar(),
    'timeout': timeout,
  }
  app[VIDEO_SESSION] = ClientSession(**session_options)
  app[AUDIO_SESSION] = ClientSession(**session_options)
  app[AUTH_SESSION] = ClientSession(**session_options)
  app[MEDIA_CACHE] = {}
  try:
    yield
  finally:
    await asyncio.gather(
      app[VIDEO_SESSION].close(),
      app[AUDIO_SESSION].close(),
      app[AUTH_SESSION].close(),
    )


def setup_proxy(app: web.Application) -> None:
  app.cleanup_ctx.append(proxy_sessions)


def _cache_manifest_sources(
  app: web.Application,
  media,
  audio_id: str,
  video_format_id: str,
) -> None:
  expires_at = time.monotonic() + 600
  video_format = media.formats[video_format_id]
  audio_format = media.formats[audio_id]
  if video_format is None or not video_format.vcodec or video_format.acodec:
    raise ValueError(f'Video format {video_format_id} is unavailable')
  if audio_format is None or not audio_format.acodec:
    raise ValueError(f'Audio format {audio_id} is unavailable')
  sources = [('video', video_format), ('audio', audio_format)]

  for kind, media_format in sources:
    app[MEDIA_CACHE][(media.id, str(media_format.id), kind)] = (
      expires_at,
      media_format.url,
      {
        str(key): str(value)
        for key, value in media_format.http_headers.items()
      },
    )


async def _detect_segment_ranges(
  app: web.Application,
  media,
  audio_id: str,
  video_format_id: str,
) -> dict[str, tuple[tuple[int, int], tuple[int, int]]]:
  async def detect(kind: str, format_id: str):
    media_format = media.formats[format_id]
    headers = {
      str(key): str(value)
      for key, value in media_format.http_headers.items()
    }
    headers.update({
      'Accept-Encoding': 'identity',
      'Range': f'bytes=0-{MP4_PROBE_MAX_SIZE - 1}',
    })
    session = app[VIDEO_SESSION if kind == 'video' else AUDIO_SESSION]
    async with session.get(
      media_format.url,
      headers=headers,
      allow_redirects=True,
    ) as response:
      if response.status not in (200, 206):
        raise ValueError(
          f'Unable to inspect format {format_id}: HTTP {response.status}',
        )

      data = bytearray()
      while len(data) < MP4_PROBE_MAX_SIZE:
        chunk = await response.content.read(
          min(MP4_PROBE_CHUNK_SIZE, MP4_PROBE_MAX_SIZE - len(data)),
        )
        if not chunk:
          break
        data.extend(chunk)
        try:
          return format_id, _parse_segment_ranges(data)
        except ValueError:
          pass

      try:
        return format_id, _parse_segment_ranges(data)
      except ValueError as ex:
        raise ValueError(
          f'Unable to locate MP4 sidx box within the first '
          f'{len(data)} bytes of format {format_id}',
        ) from ex

  detected = await asyncio.gather(
    detect('video', video_format_id),
    detect('audio', audio_id),
  )
  return dict(detected)


async def _refresh_media_source(
  app: web.Application,
  video_id: str,
  format_id: str,
  kind: str,
) -> tuple[str, dict[str, str]]:
  media_url, upstream_headers = await asyncio.to_thread(
    _resolve_media,
    video_id,
    format_id,
    kind,
  )
  app[MEDIA_CACHE][(video_id, format_id, kind)] = (
    time.monotonic() + 600,
    media_url,
    dict(upstream_headers),
  )
  return media_url, upstream_headers


async def manifest(request: web.Request) -> web.Response:
  video_id = request.match_info.get('id')
  video_format_id = request.match_info.get('format_id')
  if not VIDEO_ID_RE.fullmatch(video_id):
    raise web.HTTPBadRequest(text='Invalid YouTube video ID')
  if not FORMAT_ID_RE.fullmatch(video_format_id):
    raise web.HTTPBadRequest(text='Invalid yt-dlp video format ID')
  playback_token = _require_playback_token(request, video_id)

  audio_id = os.getenv('DEFAULT_AUDIO_ID')
  if not audio_id or not FORMAT_ID_RE.fullmatch(audio_id):
    raise web.HTTPInternalServerError(text='DEFAULT_AUDIO_ID is not configured')

  from src import youtube

  try:
    media = await asyncio.to_thread(youtube.find, video_id)
    _cache_manifest_sources(request.app, media, audio_id, video_format_id)
    segment_ranges = await _detect_segment_ranges(
      request.app,
      media,
      audio_id,
      video_format_id,
    )
    body = _build_manifest(
      video_id,
      media,
      audio_id,
      video_format_id,
      segment_ranges,
      playback_token,
    )
  except (ClientError, DownloadError, TypeError, ValueError) as ex:
    logging.warning('Unable to build DASH manifest for %s: %s', video_id, ex)
    raise web.HTTPBadGateway(text='Unable to build DASH manifest') from ex

  return _manifest_response(request, body)


async def stream_media(request: web.Request) -> web.StreamResponse:
  kind = request.match_info['kind']
  video_id = request.match_info['id']
  format_id = request.match_info['format_id']

  if kind not in ('video', 'audio'):
    raise web.HTTPNotFound(text='Unknown proxy stream type')
  if not VIDEO_ID_RE.fullmatch(video_id):
    raise web.HTTPBadRequest(text='Invalid YouTube video ID')
  if not FORMAT_ID_RE.fullmatch(format_id):
    raise web.HTTPBadRequest(text='Invalid yt-dlp format ID')
  _require_playback_token(request, video_id)

  cache_key = (video_id, format_id, kind)
  cached = request.app[MEDIA_CACHE].get(cache_key)
  if cached and cached[0] > time.monotonic():
    _, media_url, upstream_headers = cached
    upstream_headers = dict(upstream_headers)
  else:
    request.app[MEDIA_CACHE].pop(cache_key, None)
    try:
      media_url, upstream_headers = await _refresh_media_source(
        request.app,
        video_id,
        format_id,
        kind,
      )
    except (DownloadError, ValueError) as ex:
      logging.warning('Unable to resolve %s stream for %s: %s', kind, video_id, ex)
      raise web.HTTPBadGateway(text='Unable to resolve media stream') from ex

  upstream_headers['Accept-Encoding'] = 'identity'
  for header in FORWARDED_REQUEST_HEADERS:
    if header in request.headers:
      upstream_headers[header] = request.headers[header]

  session = request.app[VIDEO_SESSION if kind == 'video' else AUDIO_SESSION]

  try:
    for attempt in range(2):
      upstream = await session.request(
        request.method,
        media_url,
        headers=upstream_headers,
        allow_redirects=True,
      )
      if upstream.status != 403 or attempt == 1:
        break

      upstream.release()
      request.app[MEDIA_CACHE].pop(cache_key, None)
      media_url, refreshed_headers = await _refresh_media_source(
        request.app,
        video_id,
        format_id,
        kind,
      )
      upstream_headers = dict(refreshed_headers)
      upstream_headers['Accept-Encoding'] = 'identity'
      for header in FORWARDED_REQUEST_HEADERS:
        if header in request.headers:
          upstream_headers[header] = request.headers[header]

    async with upstream:
      response_headers = {
        header: upstream.headers[header]
        for header in FORWARDED_RESPONSE_HEADERS
        if header in upstream.headers
      }
      response = web.StreamResponse(
        status=upstream.status,
        reason=upstream.reason,
        headers=response_headers,
      )
      await response.prepare(request)

      if request.method != 'HEAD':
        try:
          async for chunk in upstream.content.iter_chunked(256 * 1024):
            await response.write(chunk)
        except (ConnectionResetError, BrokenPipeError):
          logging.info('Client disconnected from %s stream for %s', kind, video_id)

      return response
  except asyncio.CancelledError:
    raise
  except ClientError as ex:
    logging.warning('Upstream %s stream failed for %s: %s', kind, video_id, ex)
    raise web.HTTPBadGateway(text='Upstream media request failed') from ex
  except (DownloadError, ValueError) as ex:
    logging.warning('Unable to refresh %s stream for %s: %s', kind, video_id, ex)
    raise web.HTTPBadGateway(text='Unable to refresh media stream') from ex


async def proxy_auth(request: web.Request) -> web.Response:
  upstream_base = os.getenv('AUTH_UPSTREAM_URL', 'https://id.xho.st').rstrip('/')
  path = request.match_info.get('path', '')
  upstream_url = f'{upstream_base}/{path}'
  if request.query_string:
    upstream_url = f'{upstream_url}?{request.query_string}'

  headers = {
    header: request.headers[header]
    for header in ('Accept', 'Authorization', 'Content-Type', 'User-Agent')
    if header in request.headers
  }

  try:
    async with request.app[AUTH_SESSION].request(
      request.method,
      upstream_url,
      headers=headers,
      data=await request.read(),
      allow_redirects=False,
    ) as upstream:
      response_headers = {
        header: upstream.headers[header]
        for header in ('Cache-Control', 'Content-Type', 'Location')
        if header in upstream.headers
      }
      response = web.Response(
        status=upstream.status,
        body=await upstream.read(),
        headers=response_headers,
      )
      for cookie in upstream.headers.getall('Set-Cookie', []):
        response.headers.add('Set-Cookie', cookie)
      return response
  except ClientError as ex:
    logging.warning('Authentication upstream request failed: %s', ex)
    raise web.HTTPBadGateway(text='Authentication service is unavailable') from ex


class ProxyService:
  setup = staticmethod(setup_proxy)
  manifest = staticmethod(manifest)
  stream_media = staticmethod(stream_media)
  proxy_auth = staticmethod(proxy_auth)
