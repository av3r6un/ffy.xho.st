from yaml import safe_load
from pathlib import Path
import sys
import os


class Settings:
  ROOT = Path(os.path.dirname(__file__)) / '..'
  
  def load_settings(self) -> None:
    config_to_load = os.getenv('GENERAL_CONF')
    for cfg in config_to_load.split(','):
      config_file = (self.ROOT / 'config' / cfg).resolve()
      if not os.path.exists(config_file):
        print(f'{config_file}\'s configuration not found!')
        sys.exit(-1)
      with open(config_file, 'r', encoding='utf-8') as f:
        data = safe_load(f)
      for key, value in data.items():
        if self.__dict__.get(key):
          self.__dict__[f'__{key}'] = value
        else:
          self.__dict__[key] = value

    
