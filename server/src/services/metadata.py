from datetime import datetime as dt, timedelta as delta
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import JSRError
from src.models import Metadata
from typing import Any

class MetadataService:
  
  @classmethod
  async def create(cls, session: AsyncSession, raw: dict[str, Any]) -> str:
    m_uid = await Metadata.create_uid(session)
    metadata_expires = dt.now() + delta(hours=6)
    m = Metadata(m_uid, raw, metadata_expires)
    await m.save(session)
    return m_uid
    
  @classmethod
  async def update(cls, session: AsyncSession, uid: str, raw: dict[str, Any]) -> str:
    metadata = await Metadata.first(session, uid=uid)
    if not metadata: raise JSRError('not_found', message=f'Metadata[{uid}] not found!')
    metadata.title = raw['title']
    metadata.raw = raw
    metadata.expires_at = dt.now() + delta(hours=6)
    return uid

  @classmethod
  async def get_fresh(cls, session: AsyncSession, video_id: str) -> Metadata | None:
    metadata = await Metadata.first(session, video_id=video_id)
    return metadata if metadata and metadata.expires_at > dt.now() else None
  
  @classmethod
  async def upsert(cls, session: AsyncSession, raw: dict[str, Any]) -> str:
    m = await Metadata.first(session, video_id=raw['id'])
    if not m:
      return await cls.create(session, raw)
    if m.expires_at <= dt.now():
      return await cls.update(session, m.uid, raw)
    return m.uid
  
      
      
