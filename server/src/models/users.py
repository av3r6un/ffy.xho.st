from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from datetime import datetime as dt
from .base import Base


class User(Base):
  __tablename__ = 'users'
  
  uid: Mapped[str] = mapped_column(String(6), primary_key=True)
  email: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
  language: Mapped[str] = mapped_column(String(2), nullable=False, default='en', server_default='en')
  last_seen_at: Mapped[dt] = mapped_column(DateTime, nullable=False, default=func.now())
  
  def __init__(self, uid, **kwargs) -> None:
    self.uid = uid
  
  @property
  def json(self):
    return dict(uid=self.uid, email=self.email)
  
  def __str__(self):
    return f'<User {self.uid}>'
