from yaml import safe_load
from pathlib import Path
import sys
import os


class Settings:
  ROOT = Path(os.path.dirname(__file__)) / '..'
  
  def __init__(self) -> None:
    self._load_settings()
    
  def _load_settings(self) -> None:
    config_name = os.getenv('YT_DLP_CONF', 'yt_dlp.yaml')
    settings_file = (self.ROOT / 'config' / config_name).resolve()
    if not os.path.exists(settings_file):
      print('YT_DLP Configuration not found!')
      sys.exit(-1)
    with open(settings_file, 'r', encoding='utf-8') as f:
      data = safe_load(f)
      
    self.__dict__.update(data)
    
