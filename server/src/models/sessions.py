from sqlalchemy import String, Integer, ForeignKey, Enum, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import validates
from datetime import datetime as dt
from .base import Base, Status


class VideoSession(Base):
  __tablename__ = 'video_sessions'
  __table_args__ = (
    Index(
      'ix_video_sessions_user_video_expires',
      'user_uid',
      'video_id',
      'expires_at',
    ),
    Index('ix_video_sessions_status_created', 'status', 'created_at'),
    Index('ix_video_sessions_expires_at', 'expires_at'),
    Index('ix_video_sessions_metadata_uid', 'metadata_uid'),
  )
  
  uid: Mapped[str] = mapped_column(String(8), primary_key=True)
  user_uid: Mapped[str] = mapped_column(String(6), ForeignKey('users.uid'), nullable=False)
  video_id: Mapped[str] = mapped_column(String(11), nullable=False)
  status: Mapped[Status] = mapped_column(Enum(Status), nullable=False, default=Status.PENDING)
  metadata_uid: Mapped[str] = mapped_column(String(7), ForeignKey('metadata.uid'), nullable=True)
  error_message: Mapped[str] = mapped_column(Text, nullable=True)
  expires_at: Mapped[dt] = mapped_column(DateTime, nullable=False)
  
  def __init__(self, uid, user_uid, video_id, expires_at: dt, metadata_uid=None, **kwargs) -> None:
    self.uid = uid
    self.user_uid = user_uid
    self.video_id = video_id
    if metadata_uid:
      self.status = Status.READY
    self.metadata_uid = metadata_uid
    self.expires_at = expires_at
    
  @validates('status')
  def validate_status(self, _, value):
    return value if isinstance(value, Status) else Status(value)
  
  @property
  def json(self):
    return dict(
      uid=self.uid,
      video_id=self.video_id,
      status=self.status.value,
      expires_at=int(self.expires_at.timestamp()),
    )
