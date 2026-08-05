import re
from urllib.parse import parse_qs, urlparse
from yt_dlp import YoutubeDL
from .models import YtMedia
from pathlib import Path
import json
import os 


class Youtube:
  VIDEO_ID_RE = re.compile(r'^[A-Za-z0-9_-]{11}$')

  def __init__(self, settings, **kwargs) -> None:
    self.settings = settings
    self.DEBUG_FOLDER = Path(settings.ROOT) / 'cache'
    self.latest = None
    self.url = None
    
  @staticmethod
  def extract_id_from_url(url: str = None):
    if not isinstance(url, str) or not url.strip():
      return None

    value = url.strip()
    parsed = urlparse(value if '://' in value else f'https://{value}')
    host = (parsed.hostname or '').lower()
    video_id = None

    if host in {'youtu.be', 'www.youtu.be'}:
      video_id = parsed.path.lstrip('/').split('/', 1)[0]
    elif host == 'youtube.com' or host.endswith('.youtube.com'):
      video_id = parse_qs(parsed.query).get('v', [None])[0]
      if not video_id:
        parts = [part for part in parsed.path.split('/') if part]
        if len(parts) >= 2 and parts[0] in {'embed', 'live', 'shorts'}:
          video_id = parts[1]

    return video_id if Youtube.VIDEO_ID_RE.fullmatch(video_id or '') else None

  def __call__(self, url, *args, **kwargs) -> YtMedia:
    return self.__find(url, *args, **kwargs)
  
  def __find(self, url, *args, **kwargs) -> YtMedia:
    self.url = url
    with YoutubeDL(dict(quiet=True)) as ydl:
      data = ydl.extract_info(url, download=False)
    self._store_in_json(data)
    self.yt = YtMedia(**data)
    return self.yt
  
  def _store_in_json(self, data):
    fp = (self.DEBUG_FOLDER / 'latest_youtube.json').resolve()
    os.makedirs(self.DEBUG_FOLDER, exist_ok=True)
    with open(fp, 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=2)
  
  def find(self, id, **kwargs) -> YtMedia:
    url = f'https://youtube.com/watch?v={id}'
    return self.__find(url)
    
    
