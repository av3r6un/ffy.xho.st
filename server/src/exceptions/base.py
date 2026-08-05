from yaml import safe_load
from pathlib import Path
import os


class BaseError(Exception):
  messages: dict[str, list] = {}
  status: int = 400
  message = None
  
  def __init__(self, message = None, status = None, *args) -> None:
    super().__init__(*args)
    self.current_folder = Path(os.path.abspath(os.path.dirname(__file__)))
    self._load_messages()
    if status:
      self.status = status
    self.message = message
  
  def make_error(self, error, **kwargs):
    message, status = self.messages[error]
    if status:
      self.status = status
    if not self.message:
      self.message = ' '.join(kwargs.get(word, word) for word in message.split())
      
  def _load_messages(self):
    if self.messages:
      return

    with open((self.current_folder / 'error_messages.yaml').resolve(), 'r', encoding='utf-8') as f:
      type(self).messages = safe_load(f) or {}
  
  @property
  def json(self):
    return dict(data=dict(status='error', message=self.message), status=self.status)
  
  def __str__(self):
    return self.message
