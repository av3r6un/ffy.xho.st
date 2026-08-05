from sqlalchemy import String, ForeignKey, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime as dt
from .base import Base



class PushSubscription(Base):
  __tablename__ = 'push_subscriptions'
  __table_args__ = (
    Index('ux_push_subscriptions_endpoint', 'endpoint', unique=True),
    Index('ix_push_subscriptions_user_revoked', 'user_uid', 'revoked_at'),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_uid: Mapped[str] = mapped_column(String(6), ForeignKey('users.uid'), nullable=False)
  
  endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
  p256dh: Mapped[str] = mapped_column(String(255), nullable=False)
  auth: Mapped[str] = mapped_column(String(255), nullable=False)
  
  user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
  revoked_at: Mapped[dt] = mapped_column(DateTime, nullable=True)

  def __init__(self, user_uid: str, endpoint, p256h, auth, user_agent=None, **kwargs) -> None:
    self.user_uid = user_uid
    self.endpoint = endpoint
    self.p256dh = p256h
    self.auth = auth
    self.user_agent = user_agent


  @property
  def json(self):
    return dict(id=self.id, user_id=self.user_uid, endpoint=self.endpoint, revoked_at=int(self.revoked_at.timestamp()) if self.revoked_at else None)
