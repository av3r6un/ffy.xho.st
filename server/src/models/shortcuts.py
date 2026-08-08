from sqlalchemy import String, Integer, ForeignKey, func, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime as dt
from .base import Base


class ShortcutKey(Base):
  __tablename__ = 'shortcut_keys'
  __table_args__ = (
    Index('ix_shortcut_keys_user_revoked', 'user_uid', 'revoked_at'),
  )
  
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_uid: Mapped[str] = mapped_column(String(6), ForeignKey('users.uid'), nullable=False)
  secret_hash: Mapped[str] = mapped_column(String(255), nullable=False)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  last_used_at: Mapped[dt] = mapped_column(DateTime, nullable=False, default=func.now())
  revoked_at: Mapped[dt] = mapped_column(DateTime, nullable=True)
  
  def __init__(self, user_uid, secret_hash, name, **kwargs) -> None:
    self.user_uid = user_uid
    self.secret_hash = secret_hash
    self.name = name
    
  @property
  def lua(self):
    return int(self.last_used_at.timestamp())
  
  @property
  def ra(self):
    return int(self.revoked_at.timestamp()) if self.revoked_at else None
    
  @property
  def json(self):
    return dict(
      id=self.id,
      name=self.name,
      last_used_at=self.lua,
      revoked_at=self.ra,
    )
