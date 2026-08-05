from sqlalchemy import String, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime as dt
from .base import Base


class Metadata(Base):
  __tablename__ = 'metadata'
  __table_args__ = (
    Index('ix_metadata_expires_at', 'expires_at'),
  )
  
  uid: Mapped[str] = mapped_column(String(7), primary_key=True)
  video_id: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)
  title: Mapped[str] = mapped_column(String(100), nullable=False)
  
  raw: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

  expires_at: Mapped[dt] = mapped_column(DateTime, nullable=False)
  
  def __init__(self, uid, response, expires_at: dt, **kwargs) -> None:
    self.uid = uid
    self.video_id = response['id']
    self.title = response['title']
    self.raw = response
    self.expires_at = expires_at
    
  @property
  def ea(self):
    return int(self.expires_at.timestamp()) if self.expires_at else None
 
  @property
  def json(self):
    return dict(
      uid=self.uid, expires_at=self.ea, **self.raw
    )
  
