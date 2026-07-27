from yt_dlp import YoutubeDL
from .models import YtMedia
from pathlib import Path
import json
import os 


class Youtube:
  def __init__(self, settings, **kwargs) -> None:
    self.settings = settings
    self.DEBUG_FOLDER = Path(settings.ROOT) / 'cache'
    self.latest = None
    self.url = None
    
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
    
    
